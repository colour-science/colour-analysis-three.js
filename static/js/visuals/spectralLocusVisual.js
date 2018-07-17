import { Visual } from './visual.js';

class SpectralLocusVisual extends Visual {
    constructor(scene, settings) {
        super(scene, { ...settings, ...{ name: 'spectral-locus-visual' } });

        this._colourspace = settings.colourspace || 'sRGB';
        this._colourspaceModel = settings.colourspaceModel || 'CIE xyY';
        this._uniformColour = settings.uniformColour || undefined;
        this._uniformOpacity = settings.uniformOpacity || 0.75;
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
        throw new Error('"uniformOpacity" property is read only!');
    }

    route() {
        return (
            `/spectral-locus-visual?` +
            `colourspace=${this._colourspace}&` +
            `colourspaceModel=${this._colourspaceModel}&` +
            `uniformColour=${this._uniformColour}&`
        );
    }

    create(geometry) {
        var material = new THREE.LineBasicMaterial({
            vertexColors: THREE.VertexColors,
            transparent: this._uniformOpacity != 1.0,
            opacity: this._uniformOpacity
        });
        material.depthWrite = this._uniformOpacity != 1.0 ? false : true;

        var visual = new THREE.Line(geometry, material);
        visual.name = this.name;
        visual.visible = this.visible;

        return visual;
    }
}

export { SpectralLocusVisual };
