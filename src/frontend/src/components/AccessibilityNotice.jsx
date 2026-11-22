export default function AccessibilityNotice() {
  return (
    <section className="accessibility-notice" aria-label="Keyboard shortcuts">
      <p role="note">
        <strong>Canvas controls:</strong> Use the toolbar buttons to switch between
        Select, Add node, and Add edge modes. Press <kbd>Delete</kbd> or{' '}
        <kbd>Backspace</kbd> to remove a selected device or connection.
        Press <kbd>Escape</kbd> to cancel the current action.
      </p>
      <p role="note">
        <strong>Screen reader tip:</strong> When a device or connection is selected,
        its label, type, and properties are announced automatically. The canvas
        also announces the total number of devices and connections whenever the
        network changes.
      </p>
    </section>
  );
}
