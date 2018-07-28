import { Visual } from './visual.js';

class ImageScatterVisual extends Visual {
    constructor(parent, settings) {
        super(parent, { ...settings, ...{ name: 'image-scatter-visual' } });

        this._image = settings.image || 'SonyF35-StillLife.sRGB.exr';
        this._colourspace = settings.colourspace || 'sRGB';
        this._colourspaceModel = settings.colourspaceModel || 'CIE xyY';
        this._uniformColour = settings.uniformColour || undefined;
        this._uniformOpacity = settings.uniformOpacity || 0.75;
        this._subSampling = settings.subSampling || 25;
        this._pointSize = settings.pointSize || 0.01;
        this._saturate = settings.saturate || false;
    }

    get image() {
        return this._image;
    }

    set image(value) {
        this._image = value;
        this.add();
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

    get subSampling() {
        return this._subSampling;
    }

    set subSampling(value) {
        this._subSampling = value;
        this.add();
    }

    get pointSize() {
        return this._pointSize;
    }

    set pointSize(value) {
        this._pointSize = value;
        Object.keys(this.cache).forEach(
            function(key) {
                this.cache[key].material.size = value;
            }.bind(this)
        );
    }

    get saturate() {
        return this._saturate;
    }

    set saturate(value) {
        this._saturate = value;
        this.add();
    }

    route() {
        return (
            `/RGB-image-scatter-visual/${this._image}?` +
            `colourspace=${this._colourspace}&` +
            `colourspaceModel=${this._colourspaceModel}&` +
            `uniformColour=${this._uniformColour}&` +
            `subSampling=${this._subSampling}&` +
            `saturate=${this._saturate}&`
        );
    }

    create(geometry) {
        var material = new THREE.PointsMaterial({
            vertexColors: THREE.VertexColors,
            transparent: true,
            opacity: this._uniformOpacity,
            size: this._pointSize
        });

        var visual = new THREE.Points(geometry, material);
        visual.name = this.name;
        visual.visible = this.visible;

        return visual;
    }
}

export { ImageScatterVisual };
