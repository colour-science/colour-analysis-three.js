import { Visual } from './visual.js';
import { serverRoute } from '../common.js';

/**
 * @author Colour Developers / http://colour-science.org/
 */

class ImageScatterVisual extends Visual {
    constructor(parent, settings) {
        super(parent, { ...{ name: 'image-scatter-visual' }, ...settings });

        this._image = settings.image || 'Rose.ProPhoto.jpg';
        this._primaryColourspace = settings.primaryColourspace || 'sRGB';
        this._secondaryColourspace = settings.secondaryColourspace || 'DCI-P3';
        this._imageColourspace = settings.imageColourspace || 'Primary';
        this._imageDecodingCctf = settings.imageDecodingCctf || 'sRGB';
        this._colourspaceModel = settings.colourspaceModel || 'CIE xyY';
        this._uniformColour = settings.uniformColour || undefined;
        this._uniformOpacity = settings.uniformOpacity || 0.75;
        this._outOfPrimaryColourspaceGamut =
            settings.outOfPrimaryColourspaceGamut || false;
        this._outOfSecondaryColourspaceGamut =
            settings.outOfSecondaryColourspaceGamut || false;
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

    get imageColourspace() {
        return this._imageColourspace;
    }

    set imageColourspace(value) {
        this._imageColourspace = value;
        this.add();
    }

    get primaryColourspace() {
        return this._primaryColourspace;
    }

    set primaryColourspace(value) {
        this._primaryColourspace = value;
        this.add();
    }

    get secondaryColourspace() {
        return this._secondaryColourspace;
    }

    set secondaryColourspace(value) {
        this._secondaryColourspace = value;
        this.add();
    }

    get imageColourspace() {
        return this._imageColourspace;
    }

    set imageColourspace(value) {
        if (!['Primary', 'Secondary'].includes(value)) {
            throw new Error(
                '"imageColourspace" value must be ' +
                    'one of ["Primary", "Secondary"]!'
            );
        }

        this._imageColourspace = value;
        this.add();
    }

    get imageDecodingCctf() {
        return this._imageDecodingCctf;
    }

    set imageDecodingCctf(value) {
        this._imageDecodingCctf = value;
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

    get outOfPrimaryColourspaceGamut() {
        return this._outOfPrimaryColourspaceGamut;
    }

    set outOfPrimaryColourspaceGamut(value) {
        this._outOfPrimaryColourspaceGamut = value;
        this.add();
    }

    get outOfSecondaryColourspaceGamut() {
        return this._outOfSecondaryColourspaceGamut;
    }

    set outOfSecondaryColourspaceGamut(value) {
        this._outOfSecondaryColourspaceGamut = value;
        this.add();
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
        return serverRoute(
            `/RGB-image-scatter-visual/${this._image}?` +
                `primaryColourspace=${encodeURIComponent(
                    this._primaryColourspace
                )}&` +
                `secondaryColourspace=${encodeURIComponent(
                    this._secondaryColourspace
                )}&` +
                `imageColourspace=${encodeURIComponent(
                    this._imageColourspace
                )}&` +
                `imageDecodingCctf=${encodeURIComponent(
                    this._imageDecodingCctf
                )}&` +
                `colourspaceModel=${encodeURIComponent(
                    this._colourspaceModel
                )}&` +
                `outOfPrimaryColourspaceGamut=${
                    this._outOfPrimaryColourspaceGamut
                }&` +
                `outOfSecondaryColourspaceGamut=${
                    this._outOfSecondaryColourspaceGamut
                }&` +
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
