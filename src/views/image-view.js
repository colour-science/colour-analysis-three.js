import merge from 'deepmerge';
import { OrthographicView } from './orthographic-view.js';
import { ImageVisual } from '../visuals/image-visual.js';

/**
 * @author Colour Developers / https://www.colour-science.org/
 */

class ImageView extends OrthographicView {
    constructor(container, settings) {
        super(container, settings);

        settings = merge(
            {
                renderer: {
                    gammaOutput: true
                },
                scene: {
                    background: '#333333'
                },
                camera: { position: { x: 0, y: 1, z: 0 } },
                controls: { target: { x: 0, y: 0, z: 0 } },
                image: 'Rose.ProPhoto.jpg',
                primaryColourspace: 'sRGB',
                secondaryColourspace: 'DCI-P3',
                imageColourspace: 'Primary',
                imageDecodingCctf: 'sRGB',
                colourspaceModel: 'CIE xyY'
            },
            settings || {}
        );

        this.renderer.gammaOutput = settings.renderer.gammaOutput;

        this.scene.background = new THREE.Color(settings.scene.background);

        this.camera.position.copy(
            new THREE.Vector3(
                settings.camera.position.x,
                settings.camera.position.y,
                settings.camera.position.z
            )
        );
        this.controls.target = new THREE.Vector3(
            settings.controls.target.x,
            settings.controls.target.y,
            settings.controls.target.z
        );

        this._image = settings.image;
        this._primaryColourspace = settings.primaryColourspace;
        this._secondaryColourspace = settings.secondaryColourspace;
        this._imageColourspace = settings.imageColourspace;
        this._imageDecodingCctf = settings.imageDecodingCctf;
        this._colourspaceModel = settings.colourspaceModel;

        // The following groups are defining the rendering order.
        this._imageVisualGroup = new THREE.Group();
        this._imageVisualGroup.name = 'image-visual-group';
        this._scene.add(this._imageVisualGroup);
        this._imageVisual = undefined;

        this._imageOverlayVisualGroup = new THREE.Group();
        this._imageOverlayVisualGroup.name = 'image-overlay-visual-group';
        this._scene.add(this._imageOverlayVisualGroup);
        this._imageOverlayVisual = undefined;
    }

    get image() {
        return this._image;
    }

    set image(value) {
        this._image = value;

        if (this._imageVisual != undefined) {
            this._imageVisual.image = value;
        }

        if (this._imageOverlayVisual != undefined) {
            this._imageOverlayVisual.image = value;
        }
    }

    get primaryColourspace() {
        return this._primaryColourspace;
    }

    set primaryColourspace(value) {
        this._primaryColourspace = value;

        if (this._imageOverlayVisual != undefined) {
            this._imageOverlayVisual.primaryColourspace = value;
        }
    }

    get secondaryColourspace() {
        return this._secondaryColourspace;
    }

    set secondaryColourspace(value) {
        this._secondaryColourspace = value;

        if (this._imageOverlayVisual != undefined) {
            this._imageOverlayVisual.secondaryColourspace = value;
        }
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

        if (this._imageOverlayVisual != undefined) {
            this._imageOverlayVisual.imageColourspace = value;
        }
    }

    get imageDecodingCctf() {
        return this._imageDecodingCctf;
    }

    set imageDecodingCctf(value) {
        this._imageDecodingCctf = value;

        if (this._imageVisual != undefined) {
            this._imageVisual.imageDecodingCctf = value;
        }

        if (this._imageOverlayVisual != undefined) {
            this._imageOverlayVisual.imageDecodingCctf = value;
        }
    }

    get colourspaceModel() {
        return this._colourspaceModel;
    }

    set colourspaceModel(value) {
        this._colourspaceModel = value;
    }

    get imageVisual() {
        return this._imageVisual;
    }

    set imageVisual(value) {
        throw new Error('"imageVisual" property is read only!');
    }

    get imageOverlayVisual() {
        return this._imageOverlayVisual;
    }

    set imageOverlayVisual(value) {
        throw new Error('"imageOverlayVisual" property is read only!');
    }

    addImageVisual(settings) {
        this._imageVisual = new ImageVisual(
            this._imageVisualGroup,
            merge(
                {
                    name: 'image-visual',
                    image: this._image,
                    primaryColourspace: this._primaryColourspace,
                    secondaryColourspace: this._secondaryColourspace,
                    imageColourspace: this._imageColourspace,
                    imageDecodingCctf: this._imageDecodingCctf
                },
                settings || {}
            )
        );
        this._imageVisual.add();
    }

    addImageOverlayVisual(settings) {
        this._imageOverlayVisual = new ImageVisual(
            this._imageOverlayVisualGroup,
            merge(
                {
                    name: 'image-overlay-visual',
                    image: this._image,
                    primaryColourspace: this._primaryColourspace,
                    secondaryColourspace: this._secondaryColourspace,
                    imageColourspace: this._imageColourspace,
                    imageDecodingCctf: this._imageDecodingCctf,
                    uniformOpacity: 0.5,
                    depth: 0.5
                },
                settings || {}
            )
        );
        this._imageOverlayVisual.add();
    }

    isLoading() {
        return this._imageVisual.loading || this._imageOverlayVisual.loading;
    }

    animate() {
        if (this._imageOverlayVisual != undefined) {
            if (this._imageOverlayVisual.visual != undefined) {
                this._imageOverlayVisual.visual.material.opacity =
                    (this._imageOverlayVisual.uniformOpacity *
                        (1 + Math.sin(new Date().getTime() * 0.0015))) /
                    2;
            }
        }

        super.animate();
    }
}

export { ImageView };
