import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import "./viewer.css";

function addEdges(scene, mesh) {
  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(mesh.geometry),
    new THREE.LineBasicMaterial({ color: 0x9ed2ff })
  );
  edges.position.copy(mesh.position);
  edges.rotation.copy(mesh.rotation);
  edges.scale.copy(mesh.scale);
  scene.add(edges);
}

function BracketViewer({ params }) {
  const container = useRef(null);
  const view = useRef(null);
  const [tooltip, setTooltip] = useState({ visible: false, text: "", position: { x: 0, y: 0 } });

  useEffect(() => {
    if (!container.current || !params) return;

    const host = container.current;
    const L = params.arm_length_mm || 300;
    const W = params.width_mm || 60;
    const T = params.thickness_mm || 10;
    const ribT = params.rib_thickness_mm || 5;
    const ribH = params.rib_height_mm || 30;
    const ribL = params.rib_length_mm || 200;
    const materialKey = params.material_key || "AL6061-T6";

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf3f7fb);
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 4000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    host.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;

    const reset = () => {
      camera.position.set(L * 1.35, L * 0.85, L * 1.1);
      controls.target.set(L * 0.35, 0, 0);
      controls.update();
    };
    reset();
    view.current = reset;

    scene.add(new THREE.HemisphereLight(0xffffff, 0x6b8298, 2.3));
    const key = new THREE.DirectionalLight(0xffffff, 2.1);
    key.position.set(240, 260, 180);
    scene.add(key);

    const grid = new THREE.GridHelper(L * 2, 12, 0xc4d1df, 0xdde7ef);
    grid.position.z = -ribH - 2;
    scene.add(grid);

    const material = new THREE.MeshStandardMaterial({ color: 0x2877d9, metalness: 0.48, roughness: 0.34 });
    const plateMaterial = new THREE.MeshStandardMaterial({ color: 0x16446f, metalness: 0.42, roughness: 0.38 });

    // Arm base cube
    const arm = new THREE.Mesh(new THREE.BoxGeometry(L, W, T), material);
    arm.position.set(L / 2, 0, T / 2);
    arm.userData = { name: "Arm Base", params };
    scene.add(arm);
    addEdges(scene, arm);

    // Back plate
    const plate = new THREE.Mesh(new THREE.BoxGeometry(10, W, T + ribH), plateMaterial);
    plate.position.set(-5, 0, (T - ribH) / 2);
    plate.userData = { name: "Back Plate", params };
    scene.add(plate);
    addEdges(scene, plate);

    // Rib (if present)
    let rib = null;
    if (ribH > 0.1) {
      const shape = new THREE.Shape();
      shape.moveTo(0, 0);
      shape.lineTo(ribL, 0);
      shape.lineTo(0, -ribH);
      shape.closePath();
      const ribGeometry = new THREE.ExtrudeGeometry(shape, { depth: ribT, bevelEnabled: false });
      ribGeometry.rotateX(Math.PI / 2);
      ribGeometry.translate(0, ribT / 2, 0);
      rib = new THREE.Mesh(ribGeometry, material);
      rib.userData = { name: "Structural Rib", params };
      scene.add(rib);
      addEdges(scene, rib);
    }

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const getFaceDetails = (mesh) => {
      const name = mesh.userData.name;
      const materialProps = {
        "AL6061-T6": { yield: "276 MPa", density: "2.7 g/cm³" },
        "AL7075-T6": { yield: "503 MPa", density: "2.81 g/cm³" },
        "STEEL-A36": { yield: "250 MPa", density: "7.85 g/cm³" },
        "TI-6AL-4V": { yield: "880 MPa", density: "4.43 g/cm³" }
      };
      const mat = materialProps[materialKey] || materialProps["AL6061-T6"];

      return `Component: ${name}
Material: ${materialKey}
Yield Strength: ${mat.yield}
Density: ${mat.density}
Dimensions: ${L}mm x ${W}mm x ${T}mm`;
    };

    const onMouseMove = (event) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(scene.children.filter(c => c instanceof THREE.Mesh));

      if (intersects.length > 0) {
        const mesh = intersects[0].object;
        setTooltip({
          visible: true,
          text: getFaceDetails(mesh),
          position: { x: event.clientX + 15, y: event.clientY + 15 }
        });
      } else {
        setTooltip(prev => ({ ...prev, visible: false }));
      }
    };

    host.addEventListener("mousemove", onMouseMove);

    const resize = () => {
      const { width, height } = host.getBoundingClientRect();
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);
    resize();

    let frame;
    const animate = () => {
      controls.update();
      renderer.render(scene, camera);
      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      controls.dispose();
      renderer.dispose();
      host.replaceChildren();
      host.removeEventListener("mousemove", onMouseMove);
    };
  }, [params]);

  return (
    <section className="viewer-card" aria-label="Interactive bracket preview" style={{ position: "relative" }}>
      <div className="viewer-heading">
        <div>
          <span>3D GEOMETRY PREVIEW</span>
          <h3>Rotate, pan, and zoom the selected concept.</h3>
        </div>
        <button type="button" onClick={() => view.current?.()}>Reset view</button>
      </div>
      <div className="viewer-canvas" ref={container} style={{ width: "100%", height: "400px" }} />
      <p>Parametric display geometry from the selected dimensions. It is not a fused CAD solid or an FEA result.</p>

      {tooltip.visible && (
        <div className="tooltip" style={{
          position: "fixed",
          left: tooltip.position.x,
          top: tooltip.position.y,
          background: "rgba(0,0,0,0.8)",
          color: "white",
          padding: "8px",
          borderRadius: "4px",
          fontSize: "12px",
          pointerEvents: "none",
          zIndex: 9999
        }}>
          <div className="tooltip-content" style={{ whiteSpace: "pre-line" }}>{tooltip.text}</div>
        </div>
      )}
    </section>
  );
}

export default BracketViewer;