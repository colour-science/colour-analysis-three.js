import { Visual } from './visual.js';
import { serverRoute } from '../common.js';

/**
 * @author Colour Developers / http://colour-science.org/
 */

class ColourspaceVisual extends Visual {
    constructor(parent, settings) {
        super(parent, { ...{ name: 'colourspace-visual' }, ...settings });

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
                this.cache[key].material.opacity = value;
            }.bind(this)
        );
    }

    get wireframe() {
        return this._wireframe;
    }

    set wireframe(value) {
        this._wireframe = value;
        Object.keys(this.cache).forEach(
            function(key) {
                this.cache[key].material.wireframe = value;
            }.bind(this)
        );
    }

    get wireframeColour() {
        return this._wireframeColour;
    }

    set wireframeColour(value) {
        throw new Error('"wireframeOpacity" property is read only!');
    }

    get wireframeOpacity() {
        return this._wireframeOpacity;
    }

    set wireframeOpacity(value) {
        throw new Error('"wireframeOpacity" property is read only!');
    }

    route() {
        return serverRoute(
            `/RGB-colourspace-volume-visual?` +
            `colourspace=${encodeURIComponent(this._colourspace)}&` +
            `colourspaceModel=${encodeURIComponent(this._colourspaceModel)}&` +
            `segments=${this._segments}&` +
            `wireframe=${this._wireframe}&`
        );
    }

    create(geometry) {
        var material = new THREE.MeshBasicMaterial({
            vertexColors: THREE.VertexColors,
            transparent: true,
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
