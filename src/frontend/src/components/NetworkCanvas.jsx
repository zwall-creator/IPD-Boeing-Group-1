import { useEffect, useEffectEvent, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import { DEVICE_TYPES } from '../deviceIcons'
import './NetworkCanvas.css'

// Color Codings
// Cytoscape can't read CSS variables, so these must match index.css.
const VT_MAROON = '#861F41'
const VT_ORANGE = '#E5751F'
const HOKIE_STONE = '#75787B'
const TEXT = '#1f2933'

const MODES = [
  {
    id: 'select',
    label: 'Select',
    hint: 'Click to select · Drag to move',
  },
  {
    id: 'add-node',
    label: 'Add node',
    hint: 'Click empty space, then pick a device type',
  },
  { id: 'add-edge', label: 'Add edge', hint: 'Click the source node' },
]

// Backend fields from src/simulation/NW_Structure.py, all null for now.
// TODO: IP format (string vs list of ints)
// TODO: default values for base_sec_level, risk_level, cost and bandwidth
// TODO: allowed values for connection_type
// TODO: NW_Structure.py doesn't list device types (they come from deviceIcons.jsx)
// TODO: security devices (NW_Sec_Device) not supported yet
// TODO: build derived fields (security_level, connections, destination IP) for the backend
const NODE_FIELDS = { device_ip: null, base_sec_level: null, risk_level: null }
const EDGE_FIELDS = { cost: null, bandwidth: null, connection_type: null }

const STYLE = [
  {
    selector: 'node',
    style: {
      'background-color': VT_MAROON,
      'background-width': '58%',
      'background-height': '58%',
      label: 'data(label)',
      color: TEXT,
      'font-size': 11,
      'text-valign': 'bottom',
      'text-margin-y': 6,
    },
  },
  ...DEVICE_TYPES.map((d) => ({
    selector: `node[device_type = "${d.type}"]`,
    style: {
      shape: d.shape,
      width: d.width,
      height: d.height,
      'background-image': d.iconUrl,
      // Diamonds have less room inside, so their icon is drawn smaller.
      ...(d.shape === 'round-diamond' && {
        'background-width': '44%',
        'background-height': '44%',
      }),
    },
  })),
  {
    selector: 'edge',
    style: {
      width: 2,
      'line-color': HOKIE_STONE,
      'target-arrow-color': HOKIE_STONE,
      'target-arrow-shape': 'triangle',
      // Bezier curves A→B and B→A apart so both arrows stay visible.
      'curve-style': 'bezier',
    },
  },
  {
    // .edge-source marks the first node picked in Add edge mode.
    selector: 'node:selected, node.edge-source',
    style: { 'background-color': VT_ORANGE },
  },
  {
    selector: 'edge:selected',
    style: {
      width: 3,
      'line-color': VT_ORANGE,
      'target-arrow-color': VT_ORANGE,
    },
  },
]

export default function NetworkCanvas() {
  const containerRef = useRef(null)
  const typeMenuRef = useRef(null)
  const cyRef = useRef(null)
  const nodeCountRef = useRef(0)
  const edgeCountRef = useRef(0)
  const typeCountsRef = useRef({}) // device type -> last number used in a label
  const [mode, setMode] = useState('select')
  const [edgeSourceId, setEdgeSourceId] = useState(null)
  const [notice, setNotice] = useState(null)
  const [selectedCount, setSelectedCount] = useState(0)
  const [typeMenu, setTypeMenu] = useState(null) // { position, left, top } while placing a node

  function addNode(type) {
    const count = (typeCountsRef.current[type] ?? 0) + 1
    typeCountsRef.current[type] = count
    cyRef.current.add({
      group: 'nodes',
      data: {
        id: `n${++nodeCountRef.current}`,
        label: `${type} ${count}`,
        device_type: type,
        ...NODE_FIELDS,
      },
      position: typeMenu.position,
    })
    setTypeMenu(null)
  }

  function deleteSelected() {
    cyRef.current.$(':selected').remove() // removing a node also removes its edges
  }

  function changeMode(next) {
    if (next === mode) return
    // Unselect before the mode effect locks selection (unselect() does nothing while locked).
    cyRef.current.elements().unselect()
    setEdgeSourceId(null)
    setNotice(null)
    setTypeMenu(null)
    setMode(next)
  }

  // The Cytoscape listeners below are registered once, when the component mounts.
  // useEffectEvent lets them call these handlers and still see the current state.
  const handleTap = useEffectEvent((evt) => {
    const { cy, target } = evt
    setNotice(null)

    if (mode === 'add-node') {
      // While the menu is open, a click anywhere on the canvas just closes it.
      if (typeMenu) setTypeMenu(null)
      else if (target === cy) {
        const { x, y } = evt.renderedPosition
        const { clientWidth, clientHeight } = containerRef.current
        setTypeMenu({
          position: { ...evt.position }, // model coordinates, already adjusted for pan/zoom
          // Keep the 180×260px menu inside the canvas.
          left: Math.max(0, Math.min(x, clientWidth - 180)),
          top: Math.max(0, Math.min(y, clientHeight - 260)),
        })
      }
      return
    }

    // In Select mode, Cytoscape handles selecting and dragging by itself.
    if (mode !== 'add-edge') return

    if (target === cy) {
      setEdgeSourceId(null)
      return
    }
    if (!target.isNode()) return
    if (!edgeSourceId) {
      setEdgeSourceId(target.id())
      return
    }
    // Clicking the source node again cancels, so self-loops can't be made.
    if (target.id() !== edgeSourceId) {
      const source = cy.getElementById(edgeSourceId)
      if (source.edgesTo(target).nonempty()) {
        setNotice('Those nodes are already connected in that direction')
      } else {
        cy.add({
          group: 'edges',
          data: {
            id: `e${++edgeCountRef.current}`,
            source: edgeSourceId,
            target: target.id(),
            ...EDGE_FIELDS,
          },
        })
      }
    }
    setEdgeSourceId(null)
  })

  const handleKeyDown = useEffectEvent((e) => {
    if (e.key === 'Escape') {
      setTypeMenu(null)
      setEdgeSourceId(null)
      setNotice(null)
      cyRef.current.elements().unselect()
    } else if (
      (e.key === 'Delete' || e.key === 'Backspace') &&
      !e.target.closest('input, textarea, select, [contenteditable]')
    ) {
      deleteSelected()
    }
  })

  // Clicking outside the type menu closes it. Clicks on the canvas are left to handleTap.
  const handlePointerDown = useEffectEvent((e) => {
    if (
      typeMenu &&
      !typeMenuRef.current.contains(e.target) &&
      !containerRef.current.contains(e.target)
    ) {
      setTypeMenu(null)
    }
  })

  // React renders the empty <div ref={containerRef}> once and never puts children in it.
  // Cytoscape then draws its own <canvas> elements inside that div.
  useEffect(() => {
    const cy = cytoscape({
      container: containerRef.current,
      style: STYLE,
      minZoom: 0.2,
      maxZoom: 4,
    })
    cyRef.current = cy

    cy.on('tap', (evt) => handleTap(evt))
    cy.on('select unselect remove', () =>
      setSelectedCount(cy.$(':selected').length),
    )

    const onKeyDown = (e) => handleKeyDown(e)
    const onPointerDown = (e) => handlePointerDown(e)
    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('pointerdown', onPointerDown)

    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('pointerdown', onPointerDown)
      cy.destroy() // also handles StrictMode's double mount in dev
    }
  }, [])

  // Selecting only works in Select mode. Dragging is off in Add edge mode,
  // because a click that moves slightly would otherwise drag instead of click.
  useEffect(() => {
    cyRef.current.autounselectify(mode !== 'select')
    cyRef.current.autoungrabify(mode === 'add-edge')
  }, [mode])

  useEffect(() => {
    const cy = cyRef.current
    cy.nodes().removeClass('edge-source')
    if (edgeSourceId) cy.getElementById(edgeSourceId).addClass('edge-source')
  }, [edgeSourceId])

  let hint = MODES.find((m) => m.id === mode).hint
  if (mode === 'add-edge' && edgeSourceId)
    hint = 'Click the target node · Esc to cancel'
  if (notice) hint = notice

  return (
    <div className="network-canvas">
      <div
        ref={containerRef}
        className="network-canvas__graph"
        data-mode={mode}
        role="application"
        aria-label="Network canvas"
      />
      <div
        className="network-canvas__toolbar"
        role="toolbar"
        aria-label="Canvas tools"
      >
        {MODES.map((m) => (
          <button
            key={m.id}
            type="button"
            aria-pressed={mode === m.id}
            onClick={() => changeMode(m.id)}
          >
            {m.label}
          </button>
        ))}
        <span className="network-canvas__divider" />
        <button
          type="button"
          onClick={deleteSelected}
          disabled={selectedCount === 0}
        >
          Delete
        </button>
        <span className="network-canvas__hint" role="status">
          {hint}
        </span>
      </div>
      {typeMenu && (
        <div
          ref={typeMenuRef}
          className="network-canvas__type-menu"
          style={{ left: typeMenu.left, top: typeMenu.top }}
          role="menu"
          aria-label="Device type"
        >
          <div className="network-canvas__type-menu-title">Device type</div>
          {DEVICE_TYPES.map(({ type, Icon }, i) => (
            <button
              key={type}
              type="button"
              role="menuitem"
              autoFocus={i === 0}
              onClick={() => addNode(type)}
            >
              <Icon size={18} aria-hidden="true" />
              {type}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
