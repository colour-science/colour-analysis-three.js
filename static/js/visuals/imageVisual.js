import { Visual } from './visual.js';
import { fetchJSON } from '../common.js';

class ImageVisual extends Visual {
    constructor(parent, settings) {
        super(parent, { ...{ name: 'image-visual' }, ...settings });

        this._image = settings.image || 'SonyF35-StillLife.sRGB.exr';
        this._primaryColourspace = settings.primaryColourspace || 'sRGB';
        this._secondaryColourspace = settings.secondaryColourspace || 'DCI-P3';
        this._imageColourspace = settings.imageColourspace || 'Primary';
        this._outOfPrimaryColourspaceGamut =
            settings.outOfPrimaryColourspaceGamut || false;
        this._outOfSecondaryColourspaceGamut =
            settings.outOfSecondaryColourspaceGamut || false;
        this._saturate = settings.saturate || false;
        this._uniformOpacity = settings.uniformOpacity || 1.0;

        this._depth = settings.depth || 0;
    }

    get image() {
        return this._image;
    }

    set image(value) {
        this._image = value;
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

    get saturate() {
        return this._saturate;
    }

    set saturate(value) {
        this._saturate = value;
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

    get depth() {
        return this._depth;
    }

    set depth(value) {
        throw new Error('"depth" property is read only!');
    }

    route() {
        return (
            `/image-data/${this._image}?` +
            `primaryColourspace=${this._primaryColourspace}&` +
            `secondaryColourspace=${this._secondaryColourspace}&` +
            `imageColourspace=${this._imageColourspace}&` +
            `outOfPrimaryColourspaceGamut=${
                this._outOfPrimaryColourspaceGamut
            }&` +
            `outOfSecondaryColourspaceGamut=${
                this._outOfSecondaryColourspaceGamut
            }&` +
            `saturate=${this._saturate}`
        );
    }

    create(geometry) {
        var plane = new THREE.PlaneGeometry(
            1,
            geometry.height / geometry.width
        );

        var texture = new THREE.DataTexture(
            Float32Array.from(geometry.data),
            geometry.width,
            geometry.height,
            THREE.RGBFormat,
            THREE.FloatType
        );
        texture.needsUpdate = true;

        if (this._uniformOpacity == 1.0) {
            var material = new THREE.MeshBasicMaterial({
                map: texture
            });
        } else {
            var material = new THREE.MeshBasicMaterial({
                map: texture,
                alphaMap: texture,
                transparent: true,
                opacity: this._uniformOpacity
            });
        }

        var visual = new THREE.Mesh(plane, material);
        visual.name = this.name;
        visual.visible = this.visible;

        visual.position.set(0, this._depth, 0);
        visual.rotation.set(
            THREE.Math.degToRad(-90),
            0,
            THREE.Math.degToRad(180)
        );
        visual.scale.set(-1, 1, 1);

        return visual;
    }

    fetch(route) {
        fetchJSON(
            route,
            function(json) {
                this.visual = this.create(json);

                this.cache[route] = this.visual;

                this.parent.add(this.visual);
            }.bind(this)
        );
    }
}

export { ImageVisual };
