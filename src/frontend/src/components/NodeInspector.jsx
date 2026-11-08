import { useEffect, useState } from 'react';
import './NodeInspector.css';

const EMPTY = {
  label: '',
  device_type: 'PC',
  device_ip: '',
  base_sec_level: 0,
  risk_level: 0,
};

export default function NodeInspector({ node, onSave }) {
  const [draft, setDraft] = useState(EMPTY);

  useEffect(() => {
    setDraft(node || EMPTY);
  }, [node]);

  if (!node) {
    return (
      <div className="node-inspector node-inspector--empty" role="status">
        Select one device to view and edit its properties.
      </div>
    );
  }

  const update = (field) => (event) => {
    setDraft((current) => ({ ...current, [field]: event.target.value }));
  };

  return (
    <form
      className="node-inspector"
      aria-label={`Edit properties for ${node.label}`}
      onSubmit={(event) => {
        event.preventDefault();
        onSave(draft);
      }}
    >
      <div className="node-inspector__heading">
        <strong>Selected device</strong>
        <span>{node.id}</span>
      </div>
      <label>
        Label
        <input value={draft.label} onChange={update('label')} />
      </label>
      <label>
        Device type
        <select value={draft.device_type} onChange={update('device_type')}>
          {['PC', 'Laptop', 'Cell Phone', 'Router', 'Switch', 'Server'].map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </label>
      <label>
        IPv4 address
        <input value={draft.device_ip} onChange={update('device_ip')} placeholder="10.0.0.1" />
      </label>
      <label>
        Base security level
        <input type="number" min="0" step="0.1" value={draft.base_sec_level} onChange={update('base_sec_level')} />
      </label>
      <label>
        Risk level
        <input type="number" min="0" step="0.1" value={draft.risk_level} onChange={update('risk_level')} />
      </label>
      <button type="submit" className="btn-secondary">Apply device changes</button>
    </form>
  );
}
