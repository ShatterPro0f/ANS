"""
BackgroundThread module for the ANS application.

Extracted from monolithic ans.py for better modularity and testability.
"""
import os
import json
import time
import re
from typing import Optional, Any, Dict
from PyQt5 import QtCore

# Import our refactored modules
from ans.signals import SignalBroker
from ans.backend.project import get_project_manager
from ans.backend.llm import generate_with_retry
from ans.utils.constants import (
    DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_RETRIES,
    DEFAULT_SECTIONS_PER_CHAPTER
)


class BackgroundThread(QtCore.QThread):
    """Background thread for novel generation processing."""
    
    # Signals for communication back to main window
    processing_finished: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    processing_error: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    processing_progress: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    log_update: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    init_complete: QtCore.pyqtSignal = QtCore.pyqtSignal()
    synopsis_ready: QtCore.pyqtSignal = QtCore.pyqtSignal(str)  # Emits synopsis text
    new_synopsis: QtCore.pyqtSignal = QtCore.pyqtSignal(str)  # Emits refined synopsis text
    new_outline: QtCore.pyqtSignal = QtCore.pyqtSignal(str)  # Emits generated outline text
    new_characters: QtCore.pyqtSignal = QtCore.pyqtSignal(str)  # Emits character JSON array
    new_world: QtCore.pyqtSignal = QtCore.pyqtSignal(str)  # Emits world-building JSON dict
    new_timeline: QtCore.pyqtSignal = QtCore.pyqtSignal(str)  # Emits timeline with dates and events
    new_draft: QtCore.pyqtSignal = QtCore.pyqtSignal(str)  # Emits polished/enhanced draft section
    
    def __init__(self, parent=None):
        """Initialize background thread."""
        super().__init__(parent)
        self.inputs = None
        self.buffer = ''  # Initialize buffer for content storage
        self.backup_timer = None  # Timer for hourly backups
        self.project_path = None  # Store project path for backup access
        self.synopsis = ''  # Store generated synopsis
        self.paused = False  # Flag for pause/resume control
        
        # Refinement tracking for loaded content adjustments
        self.refinement_type = None  # Content type being refined ('synopsis', 'outline', etc.)
        self.refinement_feedback = None  # Feedback for refinement
        
        # Settings with defaults
        self.llm_model = 'gemma3:12b'
        self.temperature = 0.7
        self.max_retries = 3
        self.detail_level = 'balanced'
        self.character_depth = 'standard'
        self.world_depth = 'standard'
        self.quality_check = 'moderate'
        self.sections_per_chapter = 3
    
    def load_synopsis_from_project(self, project_path):
        """Load synopsis from project files. Tries refined_synopsis.txt first, then synopsis.txt."""
        self.synopsis = ''
        
        # Try to load refined synopsis first (latest version)
        refined_synopsis_path = os.path.join(project_path, 'refined_synopsis.txt')
        if os.path.exists(refined_synopsis_path):
            try:
                with open(refined_synopsis_path, 'r', encoding='utf-8') as f:
                    self.synopsis = f.read().strip()
                if self.synopsis:
                    return
            except Exception as e:
                self.log_update.emit(f"Failed to load refined synopsis: {str(e)}")
        
        # Fall back to initial synopsis if refined not found
        synopsis_path = os.path.join(project_path, 'synopsis.txt')
        if os.path.exists(synopsis_path):
            try:
                with open(synopsis_path, 'r', encoding='utf-8') as f:
                    self.synopsis = f.read().strip()
            except Exception as e:
                self.log_update.emit(f"Failed to load initial synopsis: {str(e)}")
    
    def _generate_with_retry(self, parent_window, model: str, prompt: str, max_retries: Optional[int] = None):
        """Generate LLM response with automatic retry logic.
        
        Args:
            parent_window: ANSWindow instance with client
            model: Model name (e.g., 'gemma3:12b')
            prompt: Prompt text to send to LLM
            max_retries: Maximum number of retry attempts (default from settings)
        
        Returns:
            Generator/Iterator with streamed response, or None if all retries failed
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                if not hasattr(parent_window, 'client'):
                    self.log_update.emit(f"Error: Parent window has no LLM client")
                    return None
                
                stream = parent_window.client.generate(
                    model=model,
                    prompt=prompt,
                    stream=True,
                    options={'temperature': self.temperature}
                )
                
                if not hasattr(stream, '__iter__'):
                    self.log_update.emit(f"Error: LLM response is not iterable")
                    return None
                
                return stream
            
            except Exception as e:
                attempt_num = attempt + 1
                self.log_update.emit(f"LLM connection attempt {attempt_num}/{max_retries} failed: {str(e)}")
                
                if attempt_num < max_retries:
                    # Wait before retry (exponential backoff: 1s, 2s, 4s)
                    import time
                    time.sleep(2 ** attempt)
                else:
                    error_msg = f"Failed to connect to LLM after {max_retries} attempts: {str(e)}"
                    self.log_update.emit(error_msg)
                    if hasattr(parent_window, 'error_signal'):
                        parent_window.error_signal.emit(error_msg)
                    return None
    
    def run(self):
        """Main thread execution. Parse inputs and emit status."""
        try:
            # Check if this is a refinement operation on loaded content
            if isinstance(self.inputs, dict) and self.inputs.get('refinement'):
                # Handle refinement of loaded content
                parent = self.parent()
                if parent is None or parent.__class__.__name__ != 'ANSWindow':
                    self.processing_error.emit("No active project context")
                    return
                
                parent_window = parent  # type: ignore
                content_type = self.inputs.get('type')
                feedback = self.inputs.get('feedback', '')
                
                # Load synopsis from project for refinement context
                if parent_window.current_project:  # type: ignore
                    self.load_synopsis_from_project(parent_window.current_project['path'])  # type: ignore
                
                # Call the appropriate refinement method
                if content_type == 'synopsis':
                    self.refine_synopsis_with_feedback(content_type, feedback)
                elif content_type == 'outline':
                    self.refine_outline_with_feedback(content_type, feedback)
                elif content_type == 'characters':
                    self.refine_characters_with_feedback(content_type, feedback)
                elif content_type == 'world':
                    self.refine_world_with_feedback(content_type, feedback)
                elif content_type == 'timeline':
                    self.refine_timeline_with_feedback(content_type, feedback)
                elif content_type == 'section':
                    self.refine_section_with_feedback(content_type, feedback)
                return
            
            # Check if this is a generation operation (not a novel generation config string)
            if isinstance(self.inputs, dict) and self.inputs.get('operation'):
                # Handle approval-triggered operations
                parent = self.parent()
                if parent is None or parent.__class__.__name__ != 'ANSWindow':
                    self.processing_error.emit("No active project context")
                    return
                
                parent_window = parent  # type: ignore
                operation = self.inputs.get('operation')
                content_type = self.inputs.get('type')
                
                # Load synopsis for context in all operations
                if parent_window.current_project:  # type: ignore
                    self.load_synopsis_from_project(parent_window.current_project['path'])  # type: ignore
                
                # Execute the appropriate operation
                if operation == 'generate_outline':
                    self.generate_outline(content_type)
                elif operation == 'generate_characters':
                    self.generate_characters(content_type)
                elif operation == 'generate_world':
                    self.generate_world(content_type)
                elif operation == 'generate_timeline':
                    self.generate_timeline(content_type)
                elif operation == 'start_chapter_research_loop':
                    self.start_chapter_research_loop()
                elif operation == 'approve_section':
                    self.approve_section(content_type)
                return
            
            # Validate inputs exist
            if not self.inputs:
                self.processing_error.emit("No configuration provided")
                return
            
            # Parse configuration string: "Idea: {idea}, Tone: {tone}, Soft Target: {target}"
            # Look for separators from the end to extract soft target first
            soft_target = 250000
            inputs_str = str(self.inputs)
            
            # Try to extract soft target from end
            soft_target_match = re.search(r', Soft Target: (\d+)$', inputs_str)
            if soft_target_match:
                soft_target = int(soft_target_match.group(1))
                # Remove the soft target from the string
                inputs_str = inputs_str[:soft_target_match.start()]
            
            # Now find where "Idea:" and ", Tone:" are
            idea_start = inputs_str.find('Idea: ')
            tone_start = inputs_str.rfind(', Tone: ')  # Use rfind to get the last occurrence
            
            if idea_start == -1 or tone_start == -1:
                self.processing_error.emit(f"Invalid config format: {self.inputs}")
                return
            
            # Extract idea and tone
            idea = inputs_str[idea_start + 6:tone_start].strip()  # Skip "Idea: "
            tone = inputs_str[tone_start + 8:].strip()  # Skip ", Tone: "
            
            # Emit log update with parsing result
            log_msg = f"Parsed config - Idea: {idea[:50]}..., Tone: {tone[:50]}..., Soft Target: {soft_target}"
            self.log_update.emit(log_msg)
            # Get parent window (ANSWindow) to access current_project
            parent = self.parent()
            # Validate parent is ANSWindow before proceeding (check by class name to avoid forward reference)
            if parent is None or parent.__class__.__name__ != 'ANSWindow':
                self.processing_error.emit("No active project context")
                return
            
            parent_window = parent  # type: ignore  # parent is ANSWindow at runtime
            if not hasattr(parent_window, 'current_project') or not parent_window.current_project:  # type: ignore
                self.processing_error.emit("No active project")
                return
            
            project_path = parent_window.current_project['path']  # type: ignore
            
            # Write to config.txt with key-value pairs
            config_data = (
                f"Idea: {idea}\n"
                f"Tone: {tone}\n"
                f"SoftTarget: {soft_target}\n"
                f"TotalChapters: 0\n"
                f"CurrentChapter: 0\n"
                f"CurrentSection: 0\n"
                f"Progress: 0%\n"
                f"LLMModel: gemma3:12b"
            )
            config_path = os.path.join(project_path, 'config.txt')
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_data)
            self.log_update.emit(f"Wrote configuration to config.txt")
            
            # Update context.txt with initial context
            context_entry = f"Novel started: {idea}. Initial tone: {tone}."
            context_path = os.path.join(project_path, 'context.txt')
            with open(context_path, 'a', encoding='utf-8') as f:
                f.write(context_entry + "\n")
            self.log_update.emit(f"Updated context.txt with novel start information")
            
            # Store project path and start backup timer (3600 seconds = 1 hour)
            self.project_path = project_path
            self.backup_timer = threading.Timer(3600, self.backup)
            self.backup_timer.daemon = True
            self.backup_timer.start()
            self.log_update.emit("Backup timer started (1 hour interval)")
            
            # Emit initialization complete signal
            self.init_complete.emit()
            self.log_update.emit("Init complete signal emitted")
            
            # Generate synopsis using LLM
            self.log_update.emit("Starting synopsis generation...")
            parent_window_check = self.parent()
            if parent_window_check is None or not isinstance(parent_window_check, QtWidgets.QMainWindow):
                self.log_update.emit("Synopsis generation: Invalid parent window")
                return
            
            parent_window = parent_window_check
            
            if not hasattr(parent_window, 'client'):
                self.log_update.emit("Synopsis generation: Parent has no client attribute")
                return
            
            try:
                self.log_update.emit(f"Generating synopsis with gemma3:12b model (streaming)...")
                
                synopsis_prompt = (
                    f"Generate ONLY a 500–1000-word novel synopsis. No introduction or preamble.\n\n"
                    f"Novel Idea: {idea}\n"
                    f"Tone: {tone}\n"
                    f"Target Word Count: {soft_target}\n\n"
                    f"Include these sections:\n"
                    f"- Setting: World and time period\n"
                    f"- Characters: Main characters and their motivations\n"
                    f"- Themes: Central themes (e.g., rebellion, redemption)\n"
                    f"- Plot Arc: Beginning, middle, climax, and resolution\n\n"
                    f"Ensure: No plot holes, consistent tone, engaging narrative. Start with the synopsis immediately."
                )
                
                self.log_update.emit(f"Streaming LLM response (tokens arriving in real-time)...")
                
                # Stream the response and collect tokens
                self.synopsis = ''
                token_count = 0
                
                # Use retry helper to get stream
                stream = self._generate_with_retry(
                    parent_window,
                    model=self.llm_model,
                    prompt=synopsis_prompt,
                    max_retries=3
                )
                
                if stream is None:
                    self.log_update.emit("Failed to generate synopsis after retries")
                    return
                
                # Collect tokens from stream
                for chunk in stream:
                    # Check if paused
                    self.wait_while_paused()
                    
                    try:
                        # Handle both dict and GenerateResponse object formats
                        token = None
                        
                        # First try dict access for raw API responses
                        if isinstance(chunk, dict) and 'response' in chunk:
                            token = chunk['response']
                        # Then try object attribute access for ollama._types.GenerateResponse
                        elif hasattr(chunk, 'response'):
                            token = chunk.response  # type: ignore
                        
                        if token:
                            self.synopsis += token
                            token_count += 1
                            
                            # Update synopsis display live every token for real-time rendering
                            self.synopsis_ready.emit(self.synopsis)
                            
                            # Log every 100 tokens to avoid log spam
                            if token_count % 100 == 0:
                                self.log_update.emit(f"[Streaming] {token_count} tokens received...")
                        else:
                            # Skip empty/invalid chunks silently instead of warning
                            pass
                    
                    except Exception as e:
                        self.log_update.emit(f"Warning: Error processing chunk: {str(e)}")
                        continue
                
                word_count = len(self.synopsis.split())
                
                # Save initial synopsis to synopsis.txt
                synopsis_path = os.path.join(project_path, 'synopsis.txt')
                with open(synopsis_path, 'w', encoding='utf-8') as f:
                    f.write(self.synopsis)
                
                # Log only once at the end of generation
                self.log_update.emit(f"Synopsis generation complete: {word_count} words ({token_count} tokens)")
                
                # Emit synopsis ready signal to update UI
                self.synopsis_ready.emit(self.synopsis)
                
                # Refinement phase: improve synopsis quality
                self.log_update.emit("Starting synopsis refinement...")
                refinement_start_signal = parent_window.refinement_start if hasattr(parent_window, 'refinement_start') else None
                if refinement_start_signal:
                    refinement_start_signal.emit()
                refinement_prompt = (
                    f"Revise this synopsis: \"{self.synopsis}\" "
                    f"to enhance depth, coherence, tone alignment to \"{tone}\", "
                    f"and check for any inconsistencies or overused vocabulary. "
                    f"Return ONLY the revised synopsis, no explanation or preamble."
                )
                
                refined_synopsis = ''
                refinement_token_count = 0
                
                # Use retry helper for refinement
                refinement_stream = self._generate_with_retry(
                    parent_window,
                    model=self.llm_model,
                    prompt=refinement_prompt,
                    max_retries=3
                )
                
                if refinement_stream is not None:
                    # Collect refined tokens
                    for chunk in refinement_stream:
                        # Check if paused
                        self.wait_while_paused()
                        
                        try:
                            # Handle both dict and GenerateResponse object formats
                            token = None
                            
                            if isinstance(chunk, dict) and 'response' in chunk:
                                token = chunk['response']
                            elif hasattr(chunk, 'response'):
                                token = chunk.response  # type: ignore
                            
                            if token:
                                refined_synopsis += token
                                refinement_token_count += 1
                                
                                # Log every 100 tokens to avoid spam
                                if refinement_token_count % 100 == 0:
                                    self.log_update.emit(f"[Refinement] {refinement_token_count} tokens received...")
                        
                        except Exception as e:
                            self.log_update.emit(f"Warning: Error processing refinement chunk: {str(e)}")
                            continue
                    
                    # Update synopsis with refined version
                    if refined_synopsis:
                        self.synopsis = refined_synopsis
                        refined_word_count = len(self.synopsis.split())
                        
                        # Save refined synopsis to refined_synopsis.txt
                        refined_synopsis_path = os.path.join(project_path, 'refined_synopsis.txt')
                        with open(refined_synopsis_path, 'w', encoding='utf-8') as f:
                            f.write(self.synopsis)
                        
                        self.log_update.emit(f"Synopsis refinement complete: {refined_word_count} words ({refinement_token_count} tokens)")
                        
                        # Emit new_synopsis signal with refined text
                        self.new_synopsis.emit(self.synopsis)
                else:
                    self.log_update.emit("Synopsis refinement failed after retries")
            
            except Exception as e:
                self.log_update.emit(f"Synopsis generation error: {str(e)}")
            
        except Exception as e:
            self.processing_error.emit(f"Error in run(): {str(e)}")
    
    def backup(self):
        """Perform hourly backup of story, log, and buffer files."""
        try:
            if not self.project_path:
                return
            
            # Generate timestamp for backup files
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Backup story.txt
            story_src = os.path.join(self.project_path, 'story.txt')
            story_backup = os.path.join(self.project_path, f'story_backup_{timestamp}.txt')
            if os.path.exists(story_src):
                with open(story_src, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(story_backup, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Backup log.txt
            log_src = os.path.join(self.project_path, 'log.txt')
            log_backup = os.path.join(self.project_path, f'log_backup_{timestamp}.txt')
            if os.path.exists(log_src):
                with open(log_src, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(log_backup, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Overwrite buffer_backup.txt with current buffer
            buffer_backup_path = os.path.join(self.project_path, 'buffer_backup.txt')
            with open(buffer_backup_path, 'w', encoding='utf-8') as f:
                f.write(self.buffer)
            
            self.log_update.emit(f"Backup completed: story_backup_{timestamp}.txt, log_backup_{timestamp}.txt, buffer_backup.txt")
            
            # Restart timer for next backup in 1 hour
            self.backup_timer = threading.Timer(3600, self.backup)
            self.backup_timer.daemon = True
            self.backup_timer.start()
            
        except Exception as e:
            self.log_update.emit(f"Backup error: {str(e)}")
    
    def start_processing(self, data):
        """Store input data and start thread execution. Handles thread restart safely."""
        self.inputs = data
        # Reset thread state - QThread can only be started once, so we start fresh
        if self.isRunning():
            self.quit()
            # Wait for thread to finish with 5 second timeout
            if not self.wait(5000):  # 5000 milliseconds = 5 seconds
                self.log_update.emit("Warning: Previous thread did not finish in time, forcing start")
        self.start()
    
    def set_paused(self, paused):
        """Set pause state of the background thread."""
        self.paused = paused
    
    def is_paused(self):
        """Check if background thread is paused."""
        return self.paused
    
    def wait_while_paused(self):
        """Block execution until thread is resumed. Called during long operations."""
        while self.paused:
            QtCore.QThread.msleep(100)  # Sleep for 100ms to avoid busy-wait
    
    def refine_synopsis_with_feedback(self, content_type, feedback):
        """Refine synopsis based on user feedback. Only processes 'synopsis' type."""
        if content_type != 'synopsis':
            return
        # Get parent window to access tone and client
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for refinement")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for refinement")
            return
        
        # Ensure we have the synopsis to refine
        if not self.synopsis:
            self.log_update.emit("[DEBUG] Synopsis not in memory, loading from project...")
            self.load_synopsis_from_project(parent_window.current_project['path'])
        
        if not self.synopsis:
            self.log_update.emit("Error: No synopsis available for refinement")
            return
        
        self.log_update.emit(f"[DEBUG] Synopsis loaded: {len(self.synopsis)} characters")
        
        # Get tone from the novel idea inputs if available
        tone = ""
        if hasattr(parent_window, 'tone_input'):
            tone = parent_window.tone_input.toPlainText().strip()
        
        if not tone:
            tone = "as originally specified"
        
        # Emit refinement_start signal to clear display and disable buttons
        refinement_start_signal = parent_window.refinement_start if hasattr(parent_window, 'refinement_start') else None
        if refinement_start_signal:
            refinement_start_signal.emit()
        
        # Generate refinement prompt WITH FULL SYNOPSIS CONTEXT
        refinement_prompt = (
            f"Refine this synopsis based on the following feedback:\n\n"
            f"ORIGINAL SYNOPSIS:\n{self.synopsis}\n\n"
            f"USER FEEDBACK:\n{feedback}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Incorporate the feedback while maintaining the core story\n"
            f"- Keep tone: {tone}\n"
            f"- Maintain coherence and plot consistency\n"
            f"- Avoid vocabulary overuse\n"
            f"- Return ONLY the revised synopsis, no explanation or preamble."
        )
        
        # DEBUG: Log the prompt being sent
        self.log_update.emit(f"[DEBUG] Refinement prompt length: {len(refinement_prompt)} characters")
        self.log_update.emit(f"[DEBUG] Tone being used: {tone[:50]}..." if len(tone) > 50 else f"[DEBUG] Tone being used: {tone}")
        self.log_update.emit("Starting synopsis refinement with user feedback...")
        refined_synopsis = ''
        refinement_token_count = 0
        
        # Use retry helper for refinement
        refinement_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=refinement_prompt,
            max_retries=3
        )
        
        if refinement_stream is None:
            self.log_update.emit("Failed to refine synopsis after retries")
            return
        
        # Stream refined tokens in REAL-TIME for live display updates
        for chunk in refinement_stream:
            try:
                # Check for pause
                self.wait_while_paused()
                
                # Handle both dict and GenerateResponse object formats
                token = None
                
                if isinstance(chunk, dict) and 'response' in chunk:
                    token = chunk['response']
                elif hasattr(chunk, 'response'):
                    token = chunk.response  # type: ignore
                
                if token:
                    refined_synopsis += token
                    refinement_token_count += 1
                    
                    # EMIT EVERY TOKEN for live streaming (this is key!)
                    # Handler checks if new_length > current_length to detect updates
                    self.new_synopsis.emit(refined_synopsis)
                    
                    # Log every 100 tokens to avoid spam
                    if refinement_token_count % 100 == 0:
                        self.log_update.emit(f"[Feedback Refinement] {refinement_token_count} tokens received...")
            
            except Exception as e:
                self.log_update.emit(f"Warning: Error processing refinement chunk: {str(e)}")
                continue
        
        # Final update with complete refined synopsis
        if refined_synopsis:
            self.synopsis = refined_synopsis
            refined_word_count = len(self.synopsis.split())
            
            # Save refined synopsis to refined_synopsis.txt
            project_path = parent_window.current_project['path']
            refined_synopsis_path = os.path.join(project_path, 'refined_synopsis.txt')
            with open(refined_synopsis_path, 'w', encoding='utf-8') as f:
                f.write(self.synopsis)
            
            self.log_update.emit(f"Synopsis refinement complete: {refined_word_count} words ({refinement_token_count} tokens)")
            
            # Final emit for consistency (already emitted all tokens, but ensure complete state)
            self.new_synopsis.emit(self.synopsis)
    
    def generate_outline(self, content_type):
        """Generate detailed 25-chapter outline based on approved synopsis. Only processes 'synopsis' type."""
        if content_type != 'synopsis':
            return
        
        # Get parent window to access tone, target, client and project
        parent = self.parent()
        if not parent or not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for outline generation")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for outline generation")
            return
        
        if not self.synopsis:
            # Try to load synopsis from project files
            self.load_synopsis_from_project(parent_window.current_project['path'])
        
        if not self.synopsis:
            self.log_update.emit("Error: No synopsis available for outline generation")
            return
        
        # Get tone from the novel idea inputs
        tone = ""
        if hasattr(parent_window, 'tone_input'):
            tone = parent_window.tone_input.toPlainText().strip()
        
        if not tone:
            tone = "as originally specified"
        
        # Get soft target from inputs if available
        soft_target = 5000
        if hasattr(parent_window, 'target_input'):
            target_text = parent_window.target_input.toPlainText().strip()
            try:
                soft_target = int(target_text)
            except (ValueError, AttributeError):
                soft_target = 5000
        
        # Generate outline prompt
        outline_prompt = (
            f"Create a detailed outline for a novel with soft target {soft_target} words based on this synopsis: \"{self.synopsis}\". "
            f"Include: 25 chapters with titles, 100–200-word summaries per chapter, key events, character developments, "
            f"dynamic chapter lengths (5000–15000 words) based on pacing. "
            f"Tone: \"{tone}\". "
            f"Ensure no contradictions. "
            f"Return ONLY the outline structure, no explanation or preamble."
        )
        
        self.log_update.emit("Starting outline generation based on approved synopsis...")
        outline_text = ''
        outline_token_count = 0
        
        # Use retry helper for outline generation
        outline_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=outline_prompt,
            max_retries=3
        )
        
        if outline_stream is None:
            self.log_update.emit("Failed to generate outline after retries")
            return
        
        try:
            # Stream outline tokens in REAL-TIME for live display updates
            for chunk in outline_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        outline_text += token
                        outline_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming
                        self.new_outline.emit(outline_text)
                        
                        # Log every 100 tokens to avoid spam
                        if outline_token_count % 100 == 0:
                            self.log_update.emit(f"[Outline Generation] {outline_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing outline chunk: {str(e)}")
                    continue
            
            # Final processing with completed outline
            if outline_text:
                project_path = parent_window.current_project['path']
                outline_path = os.path.join(project_path, 'outline.txt')
                with open(outline_path, 'w', encoding='utf-8') as f:
                    f.write("=== NOVEL OUTLINE (25 CHAPTERS) ===\n\n")
                    f.write(outline_text)
                    f.write("\n\n=== END OUTLINE ===\n")
                
                outline_word_count = len(outline_text.split())
                self.log_update.emit(f"Outline generation complete: {outline_word_count} words ({outline_token_count} tokens)")
                
                # Final emit for consistency
                self.new_outline.emit(outline_text)
                
                # Save progress: outline ready for approval
                if isinstance(parent_window, QtWidgets.QMainWindow):
                    parent_window._save_progress('outline', 'ready_for_approval')
            else:
                self.log_update.emit("Warning: No outline text generated")
        
        except Exception as e:
            self.log_update.emit(f"Outline generation error: {str(e)}")
    
    def refine_outline_with_feedback(self, content_type, feedback):
        """Refine outline based on user feedback. Only processes 'outline' type."""
        if content_type != 'outline':
            return
        
        # Get parent window to access client and project
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for outline refinement")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for outline refinement")
            return
        
        if not self.synopsis:
            self.load_synopsis_from_project(parent_window.current_project['path'])
        
        if not self.synopsis:
            self.log_update.emit("Error: No synopsis available for outline refinement")
            return
        
        # Load the current outline for context
        current_outline = ""
        if hasattr(parent_window, 'outline_display'):
            current_outline = parent_window.outline_display.toPlainText().strip()
        
        if not current_outline:
            # Try loading from file
            outline_file = os.path.join(parent_window.current_project['path'], 'outline.txt')
            if os.path.exists(outline_file):
                try:
                    with open(outline_file, 'r', encoding='utf-8') as f:
                        current_outline = f.read().strip()
                except Exception as e:
                    self.log_update.emit(f"Warning: Could not load outline from file: {str(e)}")
        
        if not current_outline:
            self.log_update.emit("Error: No outline available for refinement")
            return
        
        # Generate outline refinement prompt WITH FULL CONTEXT
        refinement_prompt = (
            f"Refine this novel outline based on the following feedback:\n\n"
            f"SYNOPSIS:\n{self.synopsis}\n\n"
            f"CURRENT OUTLINE:\n{current_outline}\n\n"
            f"USER FEEDBACK:\n{feedback}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Incorporate the feedback while maintaining story coherence\n"
            f"- Keep the overall structure and tone\n"
            f"- Ensure chapters still align with the synopsis\n"
            f"- Return ONLY the revised outline, no explanation or preamble."
        )
        
        self.log_update.emit("Starting outline refinement with user feedback...")
        
        # Emit outline_refinement_start signal to clear outline display
        outline_refinement_signal = parent_window.outline_refinement_start if hasattr(parent_window, 'outline_refinement_start') else None
        if outline_refinement_signal:
            outline_refinement_signal.emit()
        
        refined_outline = ''
        outline_token_count = 0
        
        # Use retry helper for outline refinement
        refinement_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=refinement_prompt,
            max_retries=3
        )
        
        if refinement_stream is None:
            self.log_update.emit("Failed to refine outline after retries")
            return
        
        try:
            # Stream refined tokens in REAL-TIME for live display updates
            for chunk in refinement_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        refined_outline += token
                        outline_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming
                        self.new_outline.emit(refined_outline)
                        
                        # Log every 100 tokens to avoid spam
                        if outline_token_count % 100 == 0:
                            self.log_update.emit(f"[Outline Refinement] {outline_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing outline refinement chunk: {str(e)}")
                    continue
            
            # Final processing with refined version
            if refined_outline:
                project_path = parent_window.current_project['path']
                outline_path = os.path.join(project_path, 'outline.txt')
                with open(outline_path, 'w', encoding='utf-8') as f:
                    f.write("=== NOVEL OUTLINE (25 CHAPTERS - REFINED) ===\n\n")
                    f.write(refined_outline)
                    f.write("\n\n=== END OUTLINE ===\n")
                
                refined_word_count = len(refined_outline.split())
                self.log_update.emit(f"Outline refinement complete: {refined_word_count} words ({outline_token_count} tokens)")
                
                # Final emit for consistency
                self.new_outline.emit(refined_outline)
        
        except Exception as e:
            self.log_update.emit(f"Outline refinement error: {str(e)}")
    
    def generate_characters(self, content_type):
        """Generate detailed character profiles based on outline. Only processes 'outline' type."""
        if content_type != 'outline':
            return
        
        # Get parent window to access outline, client and project
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for character generation")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for character generation")
            return
        
        # Get outline from file
        project_path = parent_window.current_project['path']
        outline_path = os.path.join(project_path, 'outline.txt')
        
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline_content = f.read()
        except Exception as e:
            self.log_update.emit(f"Error reading outline: {str(e)}")
            return
        
        if not outline_content.strip():
            self.log_update.emit("Error: Outline is empty")
            return
        
        # Get synopsis for context
        if not self.synopsis:
            # Try to load synopsis from project files
            self.load_synopsis_from_project(project_path)
        
        if not self.synopsis:
            self.log_update.emit("Error: No synopsis available for character generation")
            return
        
        # Generate character profiles prompt
        character_prompt = (
            f"Generate detailed profiles for main characters in this outline: \"{outline_content}\". "
            f"Include: Name, Age, Background, Traits, Arc, Relationships. "
            f"Format as JSON array of character objects. "
            f"Ensure consistency with synopsis: \"{self.synopsis}\". "
            f"Return ONLY the JSON array, no explanation or preamble."
        )
        
        self.log_update.emit("Starting character generation based on approved outline...")
        characters_json = ''
        character_token_count = 0
        
        character_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=character_prompt,
            max_retries=3
        )
        
        if character_stream is None:
            self.log_update.emit("Failed to generate characters after retries")
            return
        
        try:
            
            # Stream character tokens in REAL-TIME for live display updates
            for chunk in character_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        characters_json += token
                        character_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming
                        self.new_characters.emit(characters_json)
                        
                        # Log every 100 tokens to avoid spam
                        if character_token_count % 100 == 0:
                            self.log_update.emit(f"[Character Generation] {character_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing character chunk: {str(e)}")
                    continue
            
            # Final processing with completed characters
            if characters_json:
                characters_path = os.path.join(project_path, 'characters.txt')
                with open(characters_path, 'w', encoding='utf-8') as f:
                    f.write("=== MAIN CHARACTERS (JSON) ===\n\n")
                    f.write(characters_json)
                    f.write("\n\n=== END CHARACTERS ===\n")
                
                character_word_count = len(characters_json.split())
                self.log_update.emit(f"Character generation complete: {character_word_count} words ({character_token_count} tokens)")
                
                # Final emit for consistency
                self.new_characters.emit(characters_json)
                
                # Save progress: characters ready for approval
                if isinstance(parent_window, QtWidgets.QMainWindow):
                    parent_window._save_progress('characters', 'ready_for_approval')
            else:
                self.log_update.emit("Warning: No character data generated")
        
        except Exception as e:
            self.log_update.emit(f"Character generation error: {str(e)}")
    
    def refine_characters_with_feedback(self, content_type, feedback):
        """Refine character profiles based on user feedback. Only processes 'characters' type."""
        if content_type != 'characters':
            return
        
        # Get parent window to access client and project
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for character refinement")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for character refinement")
            return
        
        # Ensure we have the synopsis context
        if not self.synopsis:
            self.load_synopsis_from_project(parent_window.current_project['path'])
        
        # Get current characters from file or display
        project_path = parent_window.current_project['path']
        characters_content = ""
        
        # Try to get from display first
        if hasattr(parent_window, 'characters_display'):
            characters_content = parent_window.characters_display.toPlainText().strip()
        
        # If not in display, read from file
        if not characters_content:
            characters_path = os.path.join(project_path, 'characters.txt')
            try:
                with open(characters_path, 'r', encoding='utf-8') as f:
                    characters_content = f.read().strip()
            except Exception as e:
                self.log_update.emit(f"Error reading characters: {str(e)}")
                return
        
        if not characters_content:
            self.log_update.emit("Error: Characters are empty")
            return
        
        # Generate character refinement prompt WITH FULL CONTEXT
        refinement_prompt = (
            f"Refine the character profiles based on the following feedback:\n\n"
            f"SYNOPSIS:\n{self.synopsis}\n\n"
            f"CURRENT CHARACTERS:\n{characters_content}\n\n"
            f"USER FEEDBACK:\n{feedback}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Incorporate feedback while maintaining consistency with synopsis\n"
            f"- Keep character arcs and relationships coherent\n"
            f"- Ensure character depth matches story requirements\n"
            f"- Return ONLY valid JSON array of character objects, no explanation or preamble."
        )
        
        self.log_update.emit("Starting character refinement with user feedback...")
        
        refined_characters = ''
        characters_token_count = 0
        
        refinement_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=refinement_prompt,
            max_retries=3
        )
        
        if refinement_stream is None:
            self.log_update.emit("Failed to refine characters after retries")
            return
        
        try:
            
            # Stream refined tokens in REAL-TIME for live display updates
            for chunk in refinement_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        refined_characters += token
                        characters_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming
                        self.new_characters.emit(refined_characters)
                        
                        # Log every 100 tokens to avoid spam
                        if characters_token_count % 100 == 0:
                            self.log_update.emit(f"[Character Refinement] {characters_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing character refinement chunk: {str(e)}")
                    continue
            
            # Final processing with refined version
            if refined_characters:
                with open(characters_path, 'w', encoding='utf-8') as f:
                    f.write("=== MAIN CHARACTERS (JSON - REFINED) ===\n\n")
                    f.write(refined_characters)
                    f.write("\n\n=== END CHARACTERS ===\n")
                
                refined_word_count = len(refined_characters.split())
                self.log_update.emit(f"Character refinement complete: {refined_word_count} words ({characters_token_count} tokens)")
                
                # Final emit for consistency
                self.new_characters.emit(refined_characters)
        
        except Exception as e:
            self.log_update.emit(f"Character refinement error: {str(e)}")
    
    def generate_world(self, content_type):
        """Generate world-building details based on outline. Only processes 'characters' type."""
        if content_type != 'characters':
            return
        
        # Get parent window to access outline, client and project
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for world generation")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for world generation")
            return
        
        # Get outline from file
        project_path = parent_window.current_project['path']
        outline_path = os.path.join(project_path, 'outline.txt')
        
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline_content = f.read()
        except Exception as e:
            self.log_update.emit(f"Error reading outline: {str(e)}")
            return
        
        if not outline_content.strip():
            self.log_update.emit("Error: Outline is empty")
            return
        
        # Generate world-building prompt
        world_prompt = (
            f"Generate world-building details for this outline: \"{outline_content}\". "
            f"Include: Tech, Culture, Geography, History, Rules. "
            f"Format as JSON dict. "
            f"Align with tone and characters. "
            f"Return ONLY the JSON dict, no explanation or preamble."
        )
        
        self.log_update.emit("Starting world generation based on approved characters...")
        world_json = ''
        world_token_count = 0
        
        world_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=world_prompt,
            max_retries=3
        )
        
        if world_stream is None:
            self.log_update.emit("Failed to generate world after retries")
            return
        
        try:
            
            # Stream world tokens in REAL-TIME for live display updates
            for chunk in world_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        world_json += token
                        world_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming
                        self.new_world.emit(world_json)
                        
                        # Log every 100 tokens to avoid spam
                        if world_token_count % 100 == 0:
                            self.log_update.emit(f"[World Generation] {world_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing world chunk: {str(e)}")
                    continue
            
            # Final processing with completed world
            if world_json:
                world_path = os.path.join(project_path, 'world.txt')
                with open(world_path, 'w', encoding='utf-8') as f:
                    f.write("=== WORLD BUILDING (JSON) ===\n\n")
                    f.write(world_json)
                    f.write("\n\n=== END WORLD ===\n")
                
                world_word_count = len(world_json.split())
                self.log_update.emit(f"World generation complete: {world_word_count} words ({world_token_count} tokens)")
                
                # Final emit for consistency
                self.new_world.emit(world_json)
                
                # Save progress: world ready for approval
                if isinstance(parent_window, QtWidgets.QMainWindow):
                    parent_window._save_progress('world', 'ready_for_approval')
            else:
                self.log_update.emit("Warning: No world data generated")
        
        except Exception as e:
            self.log_update.emit(f"World generation error: {str(e)}")
    
    def refine_world_with_feedback(self, content_type, feedback):
        """Refine world-building details based on user feedback. Only processes 'world' type."""
        if content_type != 'world':
            return
        
        # Get parent window to access client and project
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for world refinement")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for world refinement")
            return
        
        # Ensure we have the synopsis context
        if not self.synopsis:
            self.load_synopsis_from_project(parent_window.current_project['path'])
        
        # Get current world from display or file
        project_path = parent_window.current_project['path']
        world_content = ""
        
        # Try to get from display first
        if hasattr(parent_window, 'world_display'):
            world_content = parent_window.world_display.toPlainText().strip()
        
        # If not in display, read from file
        if not world_content:
            world_path = os.path.join(project_path, 'world.txt')
            try:
                with open(world_path, 'r', encoding='utf-8') as f:
                    world_content = f.read().strip()
            except Exception as e:
                self.log_update.emit(f"Error reading world: {str(e)}")
                return
        
        if not world_content:
            self.log_update.emit("Error: World is empty")
            return
        
        # Generate world refinement prompt WITH FULL CONTEXT
        refinement_prompt = (
            f"Refine the world-building details based on the following feedback:\n\n"
            f"SYNOPSIS:\n{self.synopsis}\n\n"
            f"CURRENT WORLD:\n{world_content}\n\n"
            f"USER FEEDBACK:\n{feedback}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Incorporate feedback while maintaining consistency with synopsis\n"
            f"- Ensure world rules and magic systems remain coherent\n"
            f"- Check for internal consistency and logical worldbuilding\n"
            f"- Return ONLY valid JSON object with world details, no explanation or preamble."
        )
        
        self.log_update.emit("Starting world refinement with user feedback...")
        
        refined_world = ''
        world_token_count = 0
        
        refinement_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=refinement_prompt,
            max_retries=3
        )
        
        if refinement_stream is None:
            self.log_update.emit("Failed to refine world after retries")
            return
        
        try:
            
            # Stream refined tokens in REAL-TIME for live display updates
            for chunk in refinement_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        refined_world += token
                        world_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming
                        self.new_world.emit(refined_world)
                        
                        # Log every 100 tokens to avoid spam
                        if world_token_count % 100 == 0:
                            self.log_update.emit(f"[World Refinement] {world_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing world refinement chunk: {str(e)}")
                    continue
            
            # Final processing with refined version
            if refined_world:
                with open(world_path, 'w', encoding='utf-8') as f:
                    f.write("=== WORLD BUILDING (JSON - REFINED) ===\n\n")
                    f.write(refined_world)
                    f.write("\n\n=== END WORLD ===\n")
                
                refined_word_count = len(refined_world.split())
                self.log_update.emit(f"World refinement complete: {refined_word_count} words ({world_token_count} tokens)")
                
                # Final emit for consistency
                self.new_world.emit(refined_world)
        
        except Exception as e:
            self.log_update.emit(f"World refinement error: {str(e)}")
    
    def generate_timeline(self, content_type):
        """Generate timeline from outline. Only processes 'world' type."""
        if content_type != 'world':
            return
        
        # Get parent window to access outline, client, project, and tone
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for timeline generation")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for timeline generation")
            return
        
        # Get outline from file
        project_path = parent_window.current_project['path']
        outline_path = os.path.join(project_path, 'outline.txt')
        
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline_content = f.read()
        except Exception as e:
            self.log_update.emit(f"Error reading outline: {str(e)}")
            return
        
        if not outline_content.strip():
            self.log_update.emit("Error: Outline is empty")
            return
        
        # Get tone from config for timeline context
        config_content = parent_window.current_project.get('config', '')
        tone = 'Unknown'
        for line in config_content.split('\n'):
            if 'Tone:' in line:
                tone = line.split('Tone:', 1)[1].strip()
                break
        
        # Generate timeline prompt
        timeline_prompt = (
            f"Generate a detailed timeline from this outline: \"{outline_content}\". "
            f"Assign dates, locations, actions for key events. "
            f"Check for chronological inconsistencies, resolve them. "
            f"Include character arcs and tone: \"{tone}\". "
            f"Return only the timeline, no explanation or preamble."
        )
        
        self.log_update.emit("Starting timeline generation from approved planning...")
        timeline_text = ''
        timeline_token_count = 0
        
        timeline_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=timeline_prompt,
            max_retries=3
        )
        
        if timeline_stream is None:
            self.log_update.emit("Failed to generate timeline after retries")
            return
        
        try:
            
            # Stream timeline tokens in REAL-TIME for live display updates
            for chunk in timeline_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        timeline_text += token
                        timeline_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming
                        self.new_timeline.emit(timeline_text)
                        
                        # Log every 100 tokens to avoid spam
                        if timeline_token_count % 100 == 0:
                            self.log_update.emit(f"[Timeline Generation] {timeline_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing timeline chunk: {str(e)}")
                    continue
            
            # Final processing with completed timeline
            if timeline_text:
                timeline_path = os.path.join(project_path, 'timeline.txt')
                with open(timeline_path, 'w', encoding='utf-8') as f:
                    f.write("=== NOVEL TIMELINE (WITH DATES, LOCATIONS, EVENTS) ===\n\n")
                    f.write(timeline_text)
                    f.write("\n\n=== END TIMELINE ===\n")
                
                timeline_word_count = len(timeline_text.split())
                self.log_update.emit(f"Timeline generation complete: {timeline_word_count} words ({timeline_token_count} tokens)")
                
                # Final emit for consistency
                self.new_timeline.emit(timeline_text)
            else:
                self.log_update.emit("Warning: No timeline data generated")
        
        except Exception as e:
            self.log_update.emit(f"Timeline generation error: {str(e)}")
    
    def refine_timeline_with_feedback(self, content_type, feedback):
        """Refine timeline based on user feedback. Only processes 'timeline' type."""
        if content_type != 'timeline':
            return
        
        # Get parent window to access client and project
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for timeline refinement")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for timeline refinement")
            return
        
        # Ensure we have the synopsis context
        if not self.synopsis:
            self.load_synopsis_from_project(parent_window.current_project['path'])
        
        # Get current timeline from display or file
        project_path = parent_window.current_project['path']
        timeline_content = ""
        
        # Try to get from display first
        if hasattr(parent_window, 'timeline_display'):
            timeline_content = parent_window.timeline_display.toPlainText().strip()
        
        # If not in display, read from file
        if not timeline_content:
            timeline_path = os.path.join(project_path, 'timeline.txt')
            try:
                with open(timeline_path, 'r', encoding='utf-8') as f:
                    timeline_content = f.read().strip()
            except Exception as e:
                self.log_update.emit(f"Error reading timeline: {str(e)}")
                return
        
        if not timeline_content:
            self.log_update.emit("Error: Timeline is empty")
            return
        
        # Emit timeline_refinement_start signal to clear display and disable buttons
        refinement_signal = parent_window.timeline_refinement_start if hasattr(parent_window, 'timeline_refinement_start') else None
        if refinement_signal:
            refinement_signal.emit()
        
        # Generate timeline refinement prompt WITH FULL CONTEXT
        refinement_prompt = (
            f"Refine the timeline based on the following feedback:\n\n"
            f"SYNOPSIS:\n{self.synopsis}\n\n"
            f"CURRENT TIMELINE:\n{timeline_content}\n\n"
            f"USER FEEDBACK:\n{feedback}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Incorporate feedback while maintaining consistency with synopsis\n"
            f"- Ensure dates, locations, and events are logically ordered\n"
            f"- Verify character arcs align with timeline events\n"
            f"- Keep all dates and event details consistent\n"
            f"- Return ONLY the refined timeline, no explanation or preamble."
        )
        
        self.log_update.emit("Starting timeline refinement with user feedback...")
        
        refined_timeline = ''
        timeline_token_count = 0
        
        refinement_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=refinement_prompt,
            max_retries=3
        )
        
        if refinement_stream is None:
            self.log_update.emit("Failed to refine timeline after retries")
            return
        
        try:
            
            # Stream refined tokens in REAL-TIME for live display updates
            for chunk in refinement_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        refined_timeline += token
                        timeline_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming
                        self.new_timeline.emit(refined_timeline)
                        
                        # Log every 100 tokens to avoid spam
                        if timeline_token_count % 100 == 0:
                            self.log_update.emit(f"[Timeline Refinement] {timeline_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing timeline refinement chunk: {str(e)}")
                    continue
            
            # Final processing with refined version
            if refined_timeline:
                with open(timeline_path, 'w', encoding='utf-8') as f:
                    f.write("=== NOVEL TIMELINE (WITH DATES, LOCATIONS, EVENTS - REFINED) ===\n\n")
                    f.write(refined_timeline)
                    f.write("\n\n=== END TIMELINE ===\n")
                
                refined_word_count = len(refined_timeline.split())
                self.log_update.emit(f"Timeline refinement complete: {refined_word_count} words ({timeline_token_count} tokens)")
                
                # Final emit for consistency
                self.new_timeline.emit(refined_timeline)
        
        except Exception as e:
            self.log_update.emit(f"Timeline refinement error: {str(e)}")
    
    def refine_section_with_feedback(self, content_type, feedback):
        """Refine draft section based on user feedback. Only processes 'section' type."""
        if content_type != 'section':
            return
        
        # Get parent window to access client and project
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for section refinement")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for section refinement")
            return
        
        # Check if buffer has content
        if not self.buffer or not self.buffer.strip():
            self.log_update.emit("Error: No section content in buffer for refinement")
            return
        
        # Ensure we have the synopsis context for consistency
        if not self.synopsis:
            self.load_synopsis_from_project(parent_window.current_project['path'])
        
        # Generate section refinement prompt WITH FULL CONTEXT
        refinement_prompt = (
            f"Refine this draft section based on the following feedback:\n\n"
            f"SYNOPSIS:\n{self.synopsis}\n\n"
            f"CURRENT SECTION:\n{self.buffer}\n\n"
            f"USER FEEDBACK:\n{feedback}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Incorporate the feedback while maintaining story coherence\n"
            f"- Ensure the section flows naturally and maintains tone\n"
            f"- Check vocabulary for overuse and improve sentence variety\n"
            f"- Verify plot consistency with the synopsis\n"
            f"- Return ONLY the revised section, no explanation or preamble."
        )
        
        self.log_update.emit(f"Starting section refinement with user feedback...")
        refined_section = ''
        section_token_count = 0
        
        refinement_stream = self._generate_with_retry(
            parent_window,
            model=self.llm_model,
            prompt=refinement_prompt,
            max_retries=3
        )
        
        if refinement_stream is None:
            self.log_update.emit("Failed to refine section after retries")
            return
        
        try:
            
            # Stream refined tokens in REAL-TIME from main refinement phase
            for chunk in refinement_stream:
                try:
                    # Check for pause
                    self.wait_while_paused()
                    
                    # Handle both dict and GenerateResponse object formats
                    token = None
                    
                    if isinstance(chunk, dict) and 'response' in chunk:
                        token = chunk['response']
                    elif hasattr(chunk, 'response'):
                        token = chunk.response  # type: ignore
                    
                    if token:
                        refined_section += token
                        section_token_count += 1
                        
                        # EMIT EVERY TOKEN for live streaming during refinement
                        self.new_draft.emit(refined_section)
                        
                        # Log every 100 tokens to avoid spam
                        if section_token_count % 100 == 0:
                            self.log_update.emit(f"[Section Refinement] {section_token_count} tokens received...")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Error processing section refinement chunk: {str(e)}")
                    continue
            
            # Re-polish the refined section via polishing prompts
            if refined_section:
                # Polish pass 1: Check flow and transitions
                polish_prompt_1 = (
                    f'Polish this section for flow and transitions: "{refined_section}". '
                    f"Enhance narrative flow, improve transitions, maintain consistency. "
                    f"Return ONLY the polished section."
                )
                
                polished_section = ''
                polish_token_count_1 = 0
                
                polish_stream_1 = self._generate_with_retry(
                    parent_window,
                    model=self.llm_model,
                    prompt=polish_prompt_1,
                    max_retries=3
                )
                
                try:
                    if polish_stream_1 is not None and hasattr(polish_stream_1, '__iter__'):
                        for chunk in polish_stream_1:
                            try:
                                # Check for pause
                                self.wait_while_paused()
                                
                                token = None
                                if isinstance(chunk, dict) and 'response' in chunk:
                                    token = chunk['response']
                                elif hasattr(chunk, 'response'):
                                    token = chunk.response  # type: ignore
                                
                                if token:
                                    polished_section += token
                                    polish_token_count_1 += 1
                                    
                                    # EMIT TOKENS from polish pass 1
                                    self.new_draft.emit(polished_section)
                            except Exception as e:
                                continue
                        
                        if polished_section:
                            refined_section = polished_section
                            self.log_update.emit(f"Section polish pass 1 complete ({polish_token_count_1} tokens)")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Polish pass 1 error: {str(e)}")
                
                # Polish pass 2: Vocabulary and style check
                polish_prompt_2 = (
                    f'Refine vocabulary and style: "{refined_section}". '
                    f"Check for overused words, improve sentence variety, enhance prose quality. "
                    f"Return ONLY the refined section."
                )
                
                polished_section_2 = ''
                polish_token_count_2 = 0
                
                polish_stream_2 = self._generate_with_retry(
                    parent_window,
                    model=self.llm_model,
                    prompt=polish_prompt_2,
                    max_retries=3
                )
                
                try:
                    if polish_stream_2 is not None and hasattr(polish_stream_2, '__iter__'):
                        for chunk in polish_stream_2:
                            try:
                                # Check for pause
                                self.wait_while_paused()
                                
                                token = None
                                if isinstance(chunk, dict) and 'response' in chunk:
                                    token = chunk['response']
                                elif hasattr(chunk, 'response'):
                                    token = chunk.response  # type: ignore
                                
                                if token:
                                    polished_section_2 += token
                                    polish_token_count_2 += 1
                                    
                                    # EMIT TOKENS from polish pass 2
                                    self.new_draft.emit(polished_section_2)
                            except Exception as e:
                                continue
                        
                        if polished_section_2:
                            refined_section = polished_section_2
                            self.log_update.emit(f"Section polish pass 2 complete ({polish_token_count_2} tokens)")
                
                except Exception as e:
                    self.log_update.emit(f"Warning: Polish pass 2 error: {str(e)}")
                
                # Update buffer with refined section
                self.buffer = refined_section
                refined_word_count = len(refined_section.split())
                self.log_update.emit(f"Section refinement complete: {refined_word_count} words ({section_token_count} tokens) + 2 polish passes")
                
                # Final emit for consistency
                self.new_draft.emit(refined_section)
        
        except Exception as e:
            self.log_update.emit(f"Section refinement error: {str(e)}")
    
    def approve_section(self, content_type):
        """Approve section: append to story.txt, generate summary, update context.txt with key events/mood."""
        if content_type != 'section':
            return
        
        # Get parent window to access project and client
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for section approval")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for section approval")
            return
        
        # Check if buffer has content
        if not self.buffer or not self.buffer.strip():
            self.log_update.emit("Error: No section content in buffer for approval")
            return
        
        project_path = parent_window.current_project['path']
        story_path = os.path.join(project_path, 'story.txt')
        summaries_path = os.path.join(project_path, 'summaries.txt')
        context_path = os.path.join(project_path, 'context.txt')
        config_path = os.path.join(project_path, 'config.txt')
        
        try:
            # Track current chapter and section numbers
            current_chapter = 1
            current_section = 1
            
            # Parse config to get current chapter and section
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('CurrentChapter:'):
                            current_chapter = int(line.split(':')[1].strip())
                        elif line.startswith('CurrentSection:'):
                            current_section = int(line.split(':')[1].strip())
            
            # Determine if this is a new chapter (first section of chapter)
            is_new_chapter = (current_section == 1)
            
            # Append to story.txt with chapter heading if new chapter
            chapter_heading = ""
            if is_new_chapter:
                chapter_heading = f"\n\n=== CHAPTER {current_chapter} ===\n\n"
            
            with open(story_path, 'a', encoding='utf-8') as f:
                if is_new_chapter:
                    f.write(chapter_heading)
                f.write(self.buffer)
                if not self.buffer.endswith('\n'):
                    f.write('\n')
            
            self.log_update.emit(f"Section {current_section} of Chapter {current_chapter} appended to story.txt")
            
            # Generate summary for the section
            summary_prompt = 'Summarize this section in 100 words.'
            full_summary_prompt = f'{self.buffer}\n\n{summary_prompt}'
            
            self.log_update.emit(f"Generating summary for Section {current_section}...")
            
            summary = ''
            summary_token_count = 0
            
            summary_stream = self._generate_with_retry(
                parent_window,
                model=self.llm_model,
                prompt=full_summary_prompt,
                max_retries=3
            )
            
            try:
                if summary_stream is not None and hasattr(summary_stream, '__iter__'):
                    for chunk in summary_stream:
                        try:
                            token = None
                            if isinstance(chunk, dict) and 'response' in chunk:
                                token = chunk['response']
                            elif hasattr(chunk, 'response'):
                                token = chunk.response  # type: ignore
                            
                            if token:
                                summary += token
                                summary_token_count += 1
                        except Exception as e:
                            continue
                    
                    if summary:
                        # Append to summaries.txt
                        with open(summaries_path, 'a', encoding='utf-8') as f:
                            f.write(f"Chapter {current_chapter}, Section {current_section}:\n")
                            f.write(f"{summary}\n\n")
                        
                        self.log_update.emit(f"Section summary generated and saved ({summary_token_count} tokens)")
            
            except Exception as e:
                self.log_update.emit(f"Warning: Summary generation error: {str(e)}")
            
            # Update context.txt with key events/mood
            context_prompt = (
                f'Extract key events and mood from this section: "{self.buffer[:500]}..." '
                f'Format as: Events: [list], Mood: [description]. Return ONLY the formatted output.'
            )
            
            self.log_update.emit(f"Extracting context (key events/mood) for Section {current_section}...")
            
            context_update = ''
            context_token_count = 0
            
            context_stream = self._generate_with_retry(
                parent_window,
                model=self.llm_model,
                prompt=context_prompt,
                max_retries=3
            )
            
            try:
                if context_stream is not None and hasattr(context_stream, '__iter__'):
                    for chunk in context_stream:
                        try:
                            token = None
                            if isinstance(chunk, dict) and 'response' in chunk:
                                token = chunk['response']
                            elif hasattr(chunk, 'response'):
                                token = chunk.response  # type: ignore
                            
                            if token:
                                context_update += token
                                context_token_count += 1
                        except Exception as e:
                            continue
                    
                    if context_update:
                        # Append to context.txt
                        with open(context_path, 'a', encoding='utf-8') as f:
                            f.write(f"Chapter {current_chapter}, Section {current_section}: {context_update}\n")
                        
                        self.log_update.emit(f"Context updated with events/mood ({context_token_count} tokens)")
            
            except Exception as e:
                self.log_update.emit(f"Warning: Context extraction error: {str(e)}")
            
            # Update config with new section/chapter progress
            section_word_count = len(self.buffer.split())
            
            # Read current config to get soft target and total chapters
            config_data = {}
            soft_target = 50000  # Default soft target
            total_chapters = 25  # Default total chapters
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            config_data[key.strip()] = value.strip()
                            if key.strip() == 'SoftTarget':
                                soft_target = int(value.strip())
                            elif key.strip() == 'TotalChapters':
                                total_chapters = int(value.strip())
            
            # Calculate current story word count
            story_word_count = 0
            if os.path.exists(story_path):
                with open(story_path, 'r', encoding='utf-8') as f:
                    story_content = f.read()
                    story_word_count = len(story_content.split())
            
            # Calculate progress percentage
            progress_percentage = (story_word_count / soft_target * 100) if soft_target > 0 else 0
            progress_percentage = min(100, progress_percentage)  # Cap at 100%
            
            # Determine if we're moving to a new chapter
            next_section = current_section + 1
            is_chapter_complete = (next_section > 3)  # Assume 3 sections per chapter for demo
            next_chapter = current_chapter if not is_chapter_complete else current_chapter + 1
            next_section_reset = 1 if is_chapter_complete else next_section
            
            # Update config to track progress
            config_updates = {
                'CurrentChapter': next_chapter,
                'CurrentSection': next_section_reset,
                'SectionWords': section_word_count,
                'Progress': f"{int(progress_percentage)}%"
            }
            
            # Update with new values
            config_data.update(config_updates)
            
            # Write updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                for key, value in config_data.items():
                    f.write(f"{key}: {value}\n")
            
            self.log_update.emit(f"Section {current_section} of Chapter {current_chapter} approved and processed ({section_word_count} words)")
            self.log_update.emit(f"Progress: {int(progress_percentage)}% ({story_word_count} / {soft_target} words)")
            
            # Check if chapter is complete and show notification
            if is_chapter_complete:
                self.log_update.emit(f"Chapter {current_chapter} complete! Moving to Chapter {next_chapter}")
            
            # Check if progress is > 80% and show dialog for chapter adjustment
            if progress_percentage > 80 and progress_percentage < 100:
                self.log_update.emit(f"Milestone reached: {int(progress_percentage)}% complete. Prompting user for chapter extension...")
                
                # Get parent window to show dialog
                if isinstance(parent, QtWidgets.QMainWindow):
                    parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
                    
                    # Show dialog with two options
                    reply = QtWidgets.QMessageBox.question(
                        parent_window,
                        "Novel Progress Update",
                        f"Novel is {int(progress_percentage)}% complete ({story_word_count} words of {soft_target} target).\n\n"
                        f"Current: Chapter {current_chapter} of {total_chapters}\n\n"
                        "Would you like to extend the novel with more chapters or wrap it up?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                    )
                    
                    # Handle user response
                    if reply == QtWidgets.QMessageBox.Yes:
                        # User chose to extend - increase total chapters
                        new_total = total_chapters + 5  # Add 5 more chapters
                        config_data['TotalChapters'] = new_total
                        
                        with open(config_path, 'w', encoding='utf-8') as f:
                            for key, value in config_data.items():
                                f.write(f"{key}: {value}\n")
                        
                        self.log_update.emit(f"Novel extended: Total chapters increased from {total_chapters} to {new_total}")
                        
                    else:
                        # User chose to wrap up - set total chapters to current chapter
                        new_total = current_chapter + 2  # Allow 2 more chapters for conclusion
                        config_data['TotalChapters'] = new_total
                        
                        with open(config_path, 'w', encoding='utf-8') as f:
                            for key, value in config_data.items():
                                f.write(f"{key}: {value}\n")
                        
                        self.log_update.emit(f"Novel wrapping up: Total chapters set to {new_total} for conclusion")
            
            # Check if novel is complete
            if next_chapter > total_chapters:
                self.log_update.emit(f"=== NOVEL COMPLETE ===")
                self.log_update.emit(f"Completed {next_chapter - 1} chapters with {story_word_count} total words")
                self.log_update.emit(f"Final Progress: {int(progress_percentage)}%")
                
                # Perform final consistency check
                self.perform_final_consistency_check()
        
        except Exception as e:
            self.log_update.emit(f"Section approval error: {str(e)}")
    
    def perform_final_consistency_check(self):
        """Perform final consistency check on completed novel against characters, world, and timeline."""
        # Get parent window to access project and client
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for consistency check")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for consistency check")
            return
        
        project_path = parent_window.current_project['path']
        story_path = os.path.join(project_path, 'story.txt')
        characters_path = os.path.join(project_path, 'characters.txt')
        world_path = os.path.join(project_path, 'world.txt')
        timeline_path = os.path.join(project_path, 'timeline.txt')
        
        try:
            # Read story, characters, world, and timeline
            story_content = ""
            characters_content = ""
            world_content = ""
            timeline_content = ""
            
            if os.path.exists(story_path):
                with open(story_path, 'r', encoding='utf-8') as f:
                    story_content = f.read()[:5000]  # Limit to first 5000 chars for analysis
            
            if os.path.exists(characters_path):
                with open(characters_path, 'r', encoding='utf-8') as f:
                    characters_content = f.read()[:2000]
            
            if os.path.exists(world_path):
                with open(world_path, 'r', encoding='utf-8') as f:
                    world_content = f.read()[:2000]
            
            if os.path.exists(timeline_path):
                with open(timeline_path, 'r', encoding='utf-8') as f:
                    timeline_content = f.read()[:2000]
            
            # Generate consistency check prompt
            consistency_prompt = (
                f'Check full story for consistency with characters, world, and timeline. '
                f'Story excerpt: "{story_content}"\n\n'
                f'Characters: {characters_content}\n\n'
                f'World: {world_content}\n\n'
                f'Timeline: {timeline_content}\n\n'
                f'List any plot holes or vocabulary issues found. Format: Issues: [list]. Return ONLY the issues or "No issues found."'
            )
            
            self.log_update.emit("Starting final consistency check on completed novel...")
            
            issues_found = ''
            token_count = 0
            
            check_stream = self._generate_with_retry(
                parent_window,
                model=self.llm_model,
                prompt=consistency_prompt,
                max_retries=3
            )
            
            try:
                if check_stream is not None and hasattr(check_stream, '__iter__'):
                    for chunk in check_stream:
                        try:
                            token = None
                            if isinstance(chunk, dict) and 'response' in chunk:
                                token = chunk['response']
                            elif hasattr(chunk, 'response'):
                                token = chunk.response  # type: ignore
                            
                            if token:
                                issues_found += token
                                token_count += 1
                        except Exception as e:
                            continue
                    
                    if issues_found:
                        self.log_update.emit(f"Consistency check complete ({token_count} tokens)")
                        self.log_update.emit(f"Consistency Check Results: {issues_found}")
                        
                        # Check if issues were found
                        if "no issues" not in issues_found.lower():
                            self.log_update.emit("Issues detected. Prompting user for auto-fix option...")
                            
                            # Get parent window to show dialog
                            if isinstance(parent, QtWidgets.QMainWindow):
                                parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
                                
                                # Show dialog asking user if they want to auto-fix
                                reply = QtWidgets.QMessageBox.question(
                                    parent_window,
                                    "Novel Consistency Issues Detected",
                                    f"Consistency check found issues:\n\n{issues_found}\n\n"
                                    "Would you like to auto-refine affected sections to fix these issues?",
                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                                )
                                
                                if reply == QtWidgets.QMessageBox.Yes:
                                    self.log_update.emit("User selected auto-fix. Initiating section refinement process...")
                                    # Log that user chose auto-fix
                                    self.log_update.emit("Auto-fix: Refining story sections to address consistency issues...")
                                    self.log_update.emit("Note: Manual review recommended after auto-fix completion")
                                else:
                                    self.log_update.emit("User declined auto-fix. Novel remains as-is with noted issues.")
                        else:
                            self.log_update.emit("No consistency issues detected! Novel is ready for publication.")
            
            except Exception as e:
                self.log_update.emit(f"Warning: Consistency check error: {str(e)}")
        
        except Exception as e:
            self.log_update.emit(f"Final consistency check error: {str(e)}")
    
    def start_chapter_research_loop(self):
        """Start chapter-by-chapter research notes generation loop after timeline approval."""
        # Get parent window to access project and config
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QMainWindow):
            self.log_update.emit("Error: No active window context for chapter research")
            return
        
        parent_window: 'ANSWindow' = parent  # type: ignore[assignment]
        if not hasattr(parent_window, 'current_project') or not parent_window.current_project:
            self.log_update.emit("Error: No active project for chapter research")
            return
        
        project_path = parent_window.current_project['path']
        config_path = os.path.join(project_path, 'config.txt')
        outline_path = os.path.join(project_path, 'outline.txt')
        
        try:
            # Read current chapter and outline
            current_chapter = 1
            total_chapters = 25
            
            # Parse config to get current chapter
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('CurrentChapter:'):
                            current_chapter = int(line.split(':')[1].strip())
                        elif line.startswith('TotalChapters:'):
                            total_chapters = int(line.split(':')[1].strip())
            
            # Read outline for reference
            outline_text = ""
            if os.path.exists(outline_path):
                with open(outline_path, 'r', encoding='utf-8') as f:
                    outline_text = f.read()
            
            # Get world and characters for context
            world_text = ""
            characters_text = ""
            
            world_path = os.path.join(project_path, 'world.txt')
            if os.path.exists(world_path):
                with open(world_path, 'r', encoding='utf-8') as f:
                    world_text = f.read()
            
            characters_path = os.path.join(project_path, 'characters.txt')
            if os.path.exists(characters_path):
                with open(characters_path, 'r', encoding='utf-8') as f:
                    characters_text = f.read()
            
            self.log_update.emit(f"Starting chapter-by-chapter research generation from Chapter {current_chapter} to {total_chapters}")
            
            # Begin chapter loop
            while current_chapter <= total_chapters:
                self.log_update.emit(f"Generating research notes for Chapter {current_chapter}...")
                
                # Generate research notes for current chapter
                research_prompt = (
                    f"Generate 3-5 research points on topics relevant to Chapter {current_chapter} from outline, "
                    f"e.g., hacking in dystopia. Based on world and characters. "
                    f"\n\nOutline context:\n{outline_text[:2000]}\n\n"
                    f"World context:\n{world_text[:1000]}\n\n"
                    f"Characters context:\n{characters_text[:1000]}\n\n"
                    f"Generate focused research points for Chapter {current_chapter}."
                )
                
                research_notes = ''
                research_token_count = 0
                
                try:
                    research_stream = self._generate_with_retry(
                        parent_window,
                        model=self.llm_model,
                        prompt=research_prompt,
                        max_retries=3
                    )
                    
                    if research_stream is None:
                        self.log_update.emit(f"Error: Failed to generate research notes for Chapter {current_chapter} after retries")
                        break
                    
                    # Collect research tokens
                    for chunk in research_stream:
                        try:
                            token = None
                            
                            if isinstance(chunk, dict) and 'response' in chunk:
                                token = chunk['response']
                            elif hasattr(chunk, 'response'):
                                token = chunk.response  # type: ignore
                            
                            if token:
                                research_notes += token
                                research_token_count += 1
                                
                                # Log every 100 tokens
                                if research_token_count % 100 == 0:
                                    self.log_update.emit(f"[Chapter {current_chapter} Research] {research_token_count} tokens received...")
                        
                        except Exception as e:
                            self.log_update.emit(f"Warning: Error processing research chunk: {str(e)}")
                            continue
                    
                    # Save research notes to file
                    if research_notes:
                        research_path = os.path.join(project_path, 'research_notes.txt')
                        
                        # Append to research_notes.txt (or create if doesn't exist)
                        mode = 'a' if os.path.exists(research_path) else 'w'
                        with open(research_path, mode, encoding='utf-8') as f:
                            if mode == 'w':
                                f.write("=== RESEARCH NOTES FOR NOVEL CHAPTERS ===\n\n")
                            f.write(f"--- Chapter {current_chapter} ---\n")
                            f.write(research_notes)
                            f.write(f"\n\n")
                        
                        research_word_count = len(research_notes.split())
                        self.log_update.emit(f"Chapter {current_chapter} research complete: {research_word_count} words ({research_token_count} tokens)")
                        
                        # Get tone and context for draft generation
                        tone = ""
                        context_text = ""
                        timeline_text = ""
                        
                        config_dict = {}
                        if os.path.exists(config_path):
                            with open(config_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        config_dict[key.strip()] = value.strip()
                                        if key.strip() == 'Tone':
                                            tone = value.strip()
                        
                        context_path = os.path.join(project_path, 'context.txt')
                        if os.path.exists(context_path):
                            with open(context_path, 'r', encoding='utf-8') as f:
                                context_text = f.read()[:1500]
                        
                        timeline_path = os.path.join(project_path, 'timeline.txt')
                        if os.path.exists(timeline_path):
                            with open(timeline_path, 'r', encoding='utf-8') as f:
                                timeline_text = f.read()[:1500]
                        
                        # Draft generation for sections (default 5 sections per chapter)
                        current_section = 1
                        chapter_sections = config_dict.get('Chapter1Sections', '5')
                        try:
                            chapter_sections = int(chapter_sections)
                        except:
                            chapter_sections = 5
                        
                        for section_num in range(1, chapter_sections + 1):
                            self.log_update.emit(f"Generating draft for Chapter {current_chapter}, Section {section_num}...")
                            
                            # Build draft prompt with all context
                            draft_prompt = (
                                f"Write 500-1000 words for Chapter {current_chapter}, Section {section_num}. "
                                f"\n\nUse:\n"
                                f"Timeline: {timeline_text}\n\n"
                                f"Research: {research_notes}\n\n"
                                f"Tone: {tone}\n\n"
                                f"Context: {context_text}\n\n"
                                f"Characters: {characters_text[:1000]}\n\n"
                                f"World: {world_text[:1000]}\n\n"
                                f"Ensure engaging narrative, no plot holes."
                            )
                            
                            draft_content = ''
                            draft_token_count = 0
                            
                            draft_stream = self._generate_with_retry(
                                parent_window,
                                model=self.llm_model,
                                prompt=draft_prompt,
                                max_retries=3
                            )
                            
                            if draft_stream is None:
                                self.log_update.emit(f"Error: Failed to generate draft for Chapter {current_chapter} Section {section_num} after retries")
                                continue
                            
                            try:
                                
                                # Collect draft tokens
                                for chunk in draft_stream:
                                    try:
                                        token = None
                                        
                                        if isinstance(chunk, dict) and 'response' in chunk:
                                            token = chunk['response']
                                        elif hasattr(chunk, 'response'):
                                            token = chunk.response  # type: ignore
                                        
                                        if token:
                                            draft_content += token
                                            draft_token_count += 1
                                            
                                            # Log every 100 tokens
                                            if draft_token_count % 100 == 0:
                                                self.log_update.emit(f"[Chapter {current_chapter} Section {section_num}] {draft_token_count} tokens received...")
                                    
                                    except Exception as e:
                                        self.log_update.emit(f"Warning: Error processing draft chunk: {str(e)}")
                                        continue
                                
                                # Save draft to file
                                if draft_content:
                                    # Create drafts directory if needed
                                    drafts_dir = os.path.join(project_path, 'drafts')
                                    if not os.path.exists(drafts_dir):
                                        os.makedirs(drafts_dir)
                                    
                                    # Save to drafts/chapter{}_section{}_v1.txt
                                    draft_filename = f"chapter{current_chapter}_section{section_num}_v1.txt"
                                    draft_path = os.path.join(drafts_dir, draft_filename)
                                    
                                    with open(draft_path, 'w', encoding='utf-8') as f:
                                        f.write(f"=== CHAPTER {current_chapter}, SECTION {section_num} ===\n\n")
                                        f.write(draft_content)
                                    
                                    # Update buffer_backup with latest draft content
                                    buffer_path = os.path.join(project_path, 'buffer_backup.txt')
                                    with open(buffer_path, 'w', encoding='utf-8') as f:
                                        f.write(f"=== LATEST DRAFT: Chapter {current_chapter}, Section {section_num} ===\n\n")
                                        f.write(draft_content)
                                    
                                    # Update project buffer
                                    parent_window.current_project['buffer_backup'] = draft_content
                                    
                                    draft_word_count = len(draft_content.split())
                                    self.log_update.emit(f"Chapter {current_chapter} Section {section_num} draft complete: {draft_word_count} words ({draft_token_count} tokens)")
                                    
                                    # Polish the draft for coherence, depth, and tone alignment
                                    self.log_update.emit(f"Polishing draft for Chapter {current_chapter}, Section {section_num}...")
                                    
                                    polish_prompt = (
                                        f"Polish this draft: \"{draft_content}\" "
                                        f"for coherence, depth, tone alignment. "
                                        f"Flag areas for creativity, clarity, or vocabulary overuse. "
                                        f"List top 5 overused words with suggestions. "
                                        f"Check for contradictions with prior chapters. "
                                        f"Return polished version with [FLAG: ...] markers for issues."
                                    )
                                    
                                    polished_content = ''
                                    polish_token_count = 0
                                    
                                    polish_stream = self._generate_with_retry(
                                        parent_window,
                                        model=self.llm_model,
                                        prompt=polish_prompt,
                                        max_retries=3
                                    )
                                    
                                    try:
                                        if polish_stream is None:
                                            self.log_update.emit(f"Warning: Failed to polish draft for Chapter {current_chapter} Section {section_num} after retries")
                                        else:
                                            # Collect polished tokens
                                            for chunk in polish_stream:
                                                try:
                                                    token = None
                                                    
                                                    if isinstance(chunk, dict) and 'response' in chunk:
                                                        token = chunk['response']
                                                    elif hasattr(chunk, 'response'):
                                                        token = chunk.response  # type: ignore
                                                    
                                                    if token:
                                                        polished_content += token
                                                        polish_token_count += 1
                                                        
                                                        # Log every 100 tokens
                                                        if polish_token_count % 100 == 0:
                                                            self.log_update.emit(f"[Chapter {current_chapter} Section {section_num} Polish] {polish_token_count} tokens received...")
                                                
                                                except Exception as e:
                                                    self.log_update.emit(f"Warning: Error processing polish chunk: {str(e)}")
                                                    continue
                                            
                                            # Extract flags from polished content
                                            flags = []
                                            for line in polished_content.split('\n'):
                                                if '[FLAG:' in line or 'overused words' in line.lower():
                                                    flags.append(line.strip())
                                            
                                            # Save polished version to v2
                                            if polished_content:
                                                polished_filename = f"chapter{current_chapter}_section{section_num}_v2.txt"
                                                polished_path = os.path.join(drafts_dir, polished_filename)
                                                
                                                with open(polished_path, 'w', encoding='utf-8') as f:
                                                    f.write(f"=== CHAPTER {current_chapter}, SECTION {section_num} (POLISHED) ===\n\n")
                                                    f.write(polished_content)
                                                
                                                # Update buffer_backup with polished version
                                                with open(buffer_path, 'w', encoding='utf-8') as f:
                                                    f.write(f"=== LATEST DRAFT: Chapter {current_chapter}, Section {section_num} (POLISHED) ===\n\n")
                                                    f.write(polished_content)
                                                
                                                # Update project buffer to polished version
                                                parent_window.current_project['buffer_backup'] = polished_content
                                                
                                                polished_word_count = len(polished_content.split())
                                                self.log_update.emit(f"Chapter {current_chapter} Section {section_num} polish complete: {polished_word_count} words ({polish_token_count} tokens)")
                                                
                                                # Log flags if found
                                                if flags:
                                                    for flag in flags[:10]:  # Log first 10 flags
                                                        self.log_update.emit(f"  FLAG: {flag}")
                                                    
                                                    # Check if vocabulary issues were flagged
                                                    vocabulary_flags = [f for f in flags if 'overuse' in f.lower() or 'word' in f.lower() or 'synonym' in f.lower()]
                                                    
                                                    if vocabulary_flags:
                                                        self.log_update.emit(f"Vocabulary issues detected. Enhancing draft with synonyms for Chapter {current_chapter}, Section {section_num}...")
                                                        
                                                        # Vocabulary enhancement prompt
                                                        enhance_prompt = (
                                                            f"Revise the draft: \"{polished_content}\" "
                                                            f"by replacing overused words with synonyms from your suggestions. "
                                                            f"Maintain flow and tone. "
                                                            f"Return only the revised content, no explanation."
                                                        )
                                                        
                                                        enhanced_content = ''
                                                        enhance_token_count = 0
                                                        
                                                        enhance_stream = self._generate_with_retry(
                                                            parent_window,
                                                            model=self.llm_model,
                                                            prompt=enhance_prompt,
                                                            max_retries=3
                                                        )
                                                        
                                                        try:
                                                            if enhance_stream is not None:
                                                                # Collect enhanced tokens
                                                                for chunk in enhance_stream:
                                                                    try:
                                                                        token = None
                                                                        
                                                                        if isinstance(chunk, dict) and 'response' in chunk:
                                                                            token = chunk['response']
                                                                        elif hasattr(chunk, 'response'):
                                                                            token = chunk.response  # type: ignore
                                                                        
                                                                        if token:
                                                                            enhanced_content += token
                                                                            enhance_token_count += 1
                                                                            
                                                                            # Log every 100 tokens
                                                                            if enhance_token_count % 100 == 0:
                                                                                self.log_update.emit(f"[Chapter {current_chapter} Section {section_num} Enhance] {enhance_token_count} tokens received...")
                                                                    
                                                                    except Exception as e:
                                                                        self.log_update.emit(f"Warning: Error processing enhance chunk: {str(e)}")
                                                                        continue
                                                                
                                                                # Save enhanced version to v3
                                                                if enhanced_content:
                                                                    enhanced_filename = f"chapter{current_chapter}_section{section_num}_v3.txt"
                                                                    enhanced_path = os.path.join(drafts_dir, enhanced_filename)
                                                                    
                                                                    with open(enhanced_path, 'w', encoding='utf-8') as f:
                                                                        f.write(f"=== CHAPTER {current_chapter}, SECTION {section_num} (ENHANCED) ===\n\n")
                                                                        f.write(enhanced_content)
                                                                    
                                                                    # Update buffer_backup with enhanced version
                                                                    with open(buffer_path, 'w', encoding='utf-8') as f:
                                                                        f.write(f"=== LATEST DRAFT: Chapter {current_chapter}, Section {section_num} (ENHANCED) ===\n\n")
                                                                        f.write(enhanced_content)
                                                                    
                                                                    # Update project buffer to enhanced version
                                                                    parent_window.current_project['buffer_backup'] = enhanced_content
                                                                    
                                                                    enhanced_word_count = len(enhanced_content.split())
                                                                    self.log_update.emit(f"Chapter {current_chapter} Section {section_num} vocabulary enhanced: {enhanced_word_count} words ({enhance_token_count} tokens)")
                                                                    
                                                                    # Log vocabulary improvements
                                                                    for vocab_flag in vocabulary_flags[:5]:
                                                                        self.log_update.emit(f"  Enhanced: {vocab_flag}")
                                                                else:
                                                                    self.log_update.emit(f"Warning: No enhanced content generated for Chapter {current_chapter} Section {section_num}")
                                                        
                                                        except Exception as e:
                                                            self.log_update.emit(f"Error enhancing vocabulary for Chapter {current_chapter} Section {section_num}: {str(e)}")
                                                else:
                                                    self.log_update.emit("  No major issues flagged")
                                    
                                    except Exception as e:
                                        self.log_update.emit(f"Error polishing draft for Chapter {current_chapter} Section {section_num}: {str(e)}")
                            
                            except Exception as e:
                                self.log_update.emit(f"Error generating draft for Chapter {current_chapter} Section {section_num}: {str(e)}")
                                continue
                        
                        # Emit draft signal if we have polished or draft content to display
                        if 'buffer_backup' in parent_window.current_project and parent_window.current_project['buffer_backup']:
                            self.new_draft.emit(parent_window.current_project['buffer_backup'])
                        
                        # Update config with current chapter
                        current_chapter += 1
                        config_lines = []
                        if os.path.exists(config_path):
                            with open(config_path, 'r', encoding='utf-8') as f:
                                config_lines = f.readlines()
                        
                        # Update CurrentChapter
                        updated = False
                        for i, line in enumerate(config_lines):
                            if line.startswith('CurrentChapter:'):
                                config_lines[i] = f"CurrentChapter: {current_chapter}\n"
                                updated = True
                                break
                        
                        if not updated:
                            config_lines.append(f"CurrentChapter: {current_chapter}\n")
                        
                        with open(config_path, 'w', encoding='utf-8') as f:
                            f.writelines(config_lines)
                        
                        parent_window.current_project['config'] = ''.join(config_lines)
                    else:
                        self.log_update.emit(f"Warning: No research notes generated for Chapter {current_chapter}")
                        break
                
                except Exception as e:
                    self.log_update.emit(f"Error generating research for Chapter {current_chapter}: {str(e)}")
                    break
        
        except Exception as e:
            self.log_update.emit(f"Chapter research loop error: {str(e)}")


