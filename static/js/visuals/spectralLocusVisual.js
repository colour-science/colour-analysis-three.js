import { Visual } from './visual.js';

class SpectralLocusVisual extends Visual {
    constructor(parent, settings) {
        super(parent, { ...{ name: 'spectral-locus-visual' }, ...settings });

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
        this._uniformOpacity = value;
        Object.keys(this.cache).forEach(
            function(key) {
                this.cache[key].material.opacity = value;
            }.bind(this)
        );
    }

    route() {
        return (
            `/spectral-locus-visual?` +
            `colourspace=${encodeURIComponent(this._colourspace)}&` +
            `colourspaceModel=${encodeURIComponent(this._colourspaceModel)}&`
        );
    }

    create(geometry) {
        var material = new THREE.LineBasicMaterial({
            vertexColors: THREE.VertexColors,
            transparent: true,
            opacity: this._uniformOpacity
        });

        var visual = new THREE.Line(geometry, material);
        visual.name = this.name;
        visual.visible = this.visible;

        return visual;
    }
}

export { SpectralLocusVisual };
