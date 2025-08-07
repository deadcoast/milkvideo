# VideoMilker Development TODO

This document tracks development tasks, improvements, and feature requests for VideoMilker.

## ✅ Completed Features

- [x] Basic CLI interface with Click framework
- [x] Rich-based terminal UI with menu system
- [x] yt-dlp integration for video downloading
- [x] Configuration management with JSON files
- [x] Download history tracking
- [x] Batch download processing
- [x] Progress tracking and display
- [x] File organization and naming
- [x] Error handling and recovery
- [x] Type-safe configuration with Pydantic
- [x] File extension handling (fixed `.mp4` extension issue)
- [x] Day-based folder organization
- [x] Command-line options for direct downloads
- [x] Verbose logging support
- [x] Custom download path configuration

## 🚧 In Progress

- [ ] Enhanced batch processing with pause/resume functionality
- [ ] Additional UI themes and customization options
- [ ] Advanced format selection interface
- [ ] Plugin system for extensibility

## 📋 High Priority

### CLI Enhancements

- [ ] After `Enter video URL ():` prompt, add auto-download option:

  ```plaintext
  Start download? [y/n/auto] (y):
  ```

  - `auto`: Enable auto-start downloads permanently
  - `y`: Start download once
  - `n`: Cancel download

- [ ] Add custom download path configuration in settings menu
- [ ] Implement download queue management with pause/resume
- [ ] Add format preview before download

### UI Improvements

- [ ] Add keyboard shortcuts for common actions
- [ ] Implement search functionality in history
- [ ] Add download speed and ETA display
- [ ] Create more intuitive error messages
- [ ] Add confirmation dialogs for destructive actions

### Configuration

- [ ] Add configuration validation on startup
- [ ] Implement configuration migration for version updates
- [ ] Add configuration export/import functionality
- [ ] Create configuration wizard for first-time users

## 📋 Medium Priority

### Advanced Features

- [ ] Audio-only download option
- [ ] Chapter splitting functionality

### Performance

- [ ] Implement concurrent download limits
- [ ] Optimize memory usage for large batch downloads
- [ ] Add download resume for interrupted downloads

### File Management

- [ ] Add duplicate detection
- [ ] Add file cleanup utilities

## 📋 Low Priority

### User Experience

- [ ] Add GUI window notification/history system for visual feedback

### Integration

- [ ] Add support for external media libraries
- [ ] Create API for external applications
- [ ] Add webhook support for completed downloads

### Advanced Configuration

- [ ] Add proxy configuration
- [ ] Implement cookie management
- [ ] Add custom yt-dlp arguments support
- [ ] Create format preference profiles

## 🐛 Known Issues

- [ ] Some special characters in video titles may cause file naming issues
- [ ] Very long video titles may be truncated in file names
- [ ] Network timeouts need better handling
- [ ] Progress display may flicker on some terminals

## 🔧 Technical Debt

- [ ] Improve test coverage (currently ~60%)
- [ ] Add integration tests for full download workflows
- [ ] Refactor menu system for better maintainability
- [ ] Implement proper logging throughout the application
- [ ] Add type hints to all functions
- [ ] Create comprehensive error handling for all edge cases

## 📚 Documentation

- [ ] Add developer onboarding guide
- [ ] Create video tutorials for common use cases
- [ ] Add troubleshooting guide for common issues
- [ ] Create API documentation for plugin development
- [ ] Add contribution guidelines

## 🚀 Future Ideas

### Long-term Features

- [ ] Web interface for remote management
- [ ] Mobile companion app
- [ ] Integration with media servers (Plex, Jellyfin)
- [ ] Advanced post-processing pipeline
- [ ] Machine learning for format selection

### Platform Support

- [ ] macOS app bundle

### Development Guidelines

- Follow the existing code style (Black formatting)
- Add type hints to all new functions
- Write comprehensive docstrings
- Add tests for new features
- Update this TODO when completing tasks
- Keep commits atomic and well-described

## Priority Guidelines

- **High Priority**: Core functionality, user experience, critical bugs
- **Medium Priority**: Nice-to-have features, performance improvements
- **Low Priority**: Advanced features, integrations, future enhancements

This TODO is a living document. Feel free to add new items, update priorities, or mark completed tasks.
