import { Visual } from './visual.js';

class ColourspaceVisual extends Visual {
    constructor(scene, settings) {
        super(scene, settings);

        this._colourspace = settings.colourspace || 'sRGB';
        this._colourspaceModel = settings.colourspaceModel || 'CIE xyY';
        this._segments = settings.segments || 16;
        this._uniformColour = settings.uniformColour || undefined;
        this._uniformOpacity = settings.uniformOpacity || 0.75;
        this._wireframe = settings.wireframe || false;
        this._wireframeColour = settings.wireframeColour || undefined;
        this._wireframeOpacity = settings.wireframeOpacity || 1.0;
    }

    get colourspace() {
        return this._colourspace;
    }

    set colourspace(value) {
        this._colourspace = value;
        this.add();
    }

    get colourspaceModel() {
        return this._colourspaceModel;
    }

    set colourspaceModel(value) {
        this._colourspaceModel = value;
        this.add();
    }

    get segments() {
        return this._segments;
    }

    set segments(value) {
        this._segments = value;
        this.add();
    }

    get uniformColour() {
        return this._uniformColour;
    }

    set uniformColour(value) {
        this._uniformColour = value;
        this.add();
    }

    get uniformOpacity() {
        return this._uniformOpacity;
    }

    set uniformOpacity(value) {
        this._uniformOpacity = value;
        Object.keys(this.cache).forEach(
            function(key) {
                this.cache[key].material.transparent = value != 1.0,
                this.cache[key].material.opacity = value;
            }.bind(this)
        );
    }

    get wireframe() {
        return this._wireframe;
    }

    set wireframe(value) {
        this._wireframe = value;
        this.add();
    }

    set wireframeColour(value) {
        this._wireframeColour = value;
        this.add();
    }

    get wireframeOpacity() {
        return this._wireframeOpacity;
    }

    set wireframeOpacity(value) {
        throw new Error('"wireframeOpacity" property is read only!');
    }

    route() {
        return (
            `/RGB-colourspace-volume-visual?` +
            `colourspace=${this._colourspace}&` +
            `colourspaceModel=${this._colourspaceModel}&` +
            `segments=${this._segments}&` +
            `uniformColour=${this._uniformColour}&` +
            `wireframe=${this._wireframe}&` +
            `wireframeColour=${this._wireframeColour}&`
        );
    }

    create(geometry) {
        var material = new THREE.MeshBasicMaterial({
            vertexColors: THREE.VertexColors,
            transparent: this._uniformOpacity != 1.0,
            opacity: this._uniformOpacity,
            wireframe: this._wireframe
        });

        material.depthWrite = this._uniformOpacity != 1.0 ? false : true;

        var visual = new THREE.Mesh(geometry, material);
        visual.name = this.name;
        visual.visible = this.visible;

        return visual;
    }
}

export { ColourspaceVisual };
