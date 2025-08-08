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
- [x] Auto-download option after URL input
- [x] Enhanced download path configuration with folder browser
- [x] Download queue management with pause/resume functionality
- [x] Format preview and selection before download
- [x] Keyboard shortcuts for common actions
- [x] Advanced search functionality in history
- [x] Enhanced download speed and ETA display
- [x] Configuration validation on startup with auto-fix
- [x] Configuration export/import functionality
- [x] Configuration wizard for first-time users
- [x] User-friendly error messages with suggestions
- [x] Confirmation dialogs for destructive actions
- [x] Audio-only download option with multiple format support
- [x] Concurrent download limits with threading support
- [x] Chapter splitting functionality with preview
- [x] Memory optimization for large batch downloads
- [x] Download resume for interrupted downloads
- [x] Duplicate detection with multiple algorithms
- [x] Comprehensive file cleanup utilities

## 🚧 In Progress

- [ ] Enhanced batch processing with pause/resume functionality
- [ ] Additional UI themes and customization options
- [ ] Advanced format selection interface
- [ ] Plugin system for extensibility

## 📋 High Priority

### UI Improvements

- [x] Create more intuitive error messages
- [x] Add confirmation dialogs for destructive actions

### Configuration

- [x] Add configuration validation on startup
- [x] Implement configuration migration for version updates
- [x] Add configuration export/import functionality
- [x] Create configuration wizard for first-time users

## 📋 Medium Priority

### Advanced Features

- [x] Audio-only download option
- [x] Chapter splitting functionality

### Performance

- [x] Implement concurrent download limits
- [x] Optimize memory usage for large batch downloads
- [x] Add download resume for interrupted downloads

### File Management

- [x] Add duplicate detection
- [x] Add file cleanup utilities

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
