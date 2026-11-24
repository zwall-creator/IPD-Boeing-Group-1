import { useEffect, useRef } from "react";
import "./ConfirmDialog.css";

/**
 * ConfirmDialog: reusable yes/no popup for confirmation
 */
export default function ConfirmDialog({
  open, // true = show, false = hide
  title = "Are you sure?",
  message,
  onConfirm,
  onCancel,
  confirmLabel = "Yes",
  cancelLabel = "No",
}) {
  const dialogRef = useRef(null); // holds <dialog> element from page

  // When 'open' changes
  useEffect(() => {
    const dialog = dialogRef.current;
    if (open && !dialog.open) {
      dialog.showModal();
    } else if (!open && dialog.open) {
      dialog.close();
    }
  }, [open]);

  return (
    <dialog ref={dialogRef} className="confirm-dialog" onCancel={onCancel}>
      <h2 className="confirm-dialog-title">{title}</h2>
      <p className="confirm-dialog-message">{message}</p>
      <div className="confirm-dialog-buttons">
        {/* Cancel and Confirm buttons, Cancel prioritized */}
        <button type="button" className="btn-secondary" onClick={onCancel}>
          {cancelLabel}
        </button>
        <button type="button" className="btn-secondary" onClick={onConfirm}>
          {confirmLabel}
        </button>
      </div>
    </dialog>
  );
}
