import { Visual } from './visual.js';
import { fetchJSON } from '../common.js';

class ImageVisual extends Visual {
    constructor(scene, settings) {
        super(scene, { ...settings, ...{ name: 'image-visual' } });

        this._image = settings.image || 'SonyF35-StillLife.sRGB.exr';
        this._colourspace = settings.colourspace || 'sRGB';
        this._colourspaceModel = settings.colourspaceModel || 'CIE xyY';
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

    get saturate() {
        return this._saturate;
    }

    set saturate(value) {
        this._saturate = value;
        this.add();
    }

    route() {
        return `/image-data/${this._image}?saturate=${this._saturate}`;
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

        var material = new THREE.MeshBasicMaterial({
            map: texture
        });

        var visual = new THREE.Mesh(plane, material);
        visual.name = this.name;
        visual.visible = this.visible;

        visual.rotation.x = THREE.Math.degToRad(-90);
        visual.rotation.z = THREE.Math.degToRad(180);

        return visual;
    }

    fetch(route) {
        fetchJSON(
            route,
            function(json) {
                this.visual = this.create(json);

                this.cache[route] = this.visual;

                this.scene.add(this.visual);
            }.bind(this)
        );
    }
}

export { ImageVisual };
