import { Visual } from './visual.js';
import { rotateToWorld, loadingCallback } from '../common.js';

class ViewAxesVisual extends Visual {
    constructor(view, settings) {
        super(view.camera, { ...{ name: 'view-axes-visual' }, ...settings });

        this._view = view;

        this._colourspaceModel = settings.colourspaceModel || 'CIE xyY';
    }

    get view() {
        return this._view;
    }

    set view(value) {
        throw new Error('"view" property is read only!');
    }

    get colourspaceModel() {
        return this._colourspaceModel;
    }

    set colourspaceModel(value) {
        this._colourspaceModel = value;
        this.add();
    }

    route() {
        return `/colourspace-models?colourspaceModel=${this._colourspaceModel}`;
    }

    create(json) {
        var visual = new THREE.AxesHelper();
        // prettier-ignore
        visual.geometry.attributes.color.array.set([
            0, 0, 1, 0, 0, 1,
            0, 1, 0, 0, 1, 0,
            1, 0, 0, 1, 0, 0,
        ]);

        visual.name = this.name;
        visual.visible = this.visible;

        var loader = new THREE.FontLoader();
        loader.load(
            'https://cdn.rawgit.com/mrdoob/three.js/master/examples/fonts/helvetiker_regular.typeface.json',
            function(font) {
                var fontSize = 0.4;
                var fontDepth = 0.1;
                var axesLabels = [
                    {
                        text: json[this._colourspaceModel][0],
                        colour: '#FF0000',
                        position: {
                            x: -fontSize / 2,
                            y: -fontSize / 2,
                            z: 1 + fontSize / 2
                        }
                    },
                    {
                        text: json[this._colourspaceModel][1],
                        colour: '#00FF00',
                        position: {
                            x: -fontSize / 2,
                            y: 1 + fontSize / 2,
                            z: -fontDepth / 2
                        }
                    },
                    {
                        text: json[this._colourspaceModel][2],
                        colour: '#0000FF',
                        position: {
                            x: 1 + fontSize / 2,
                            y: -fontSize / 2,
                            z: -fontDepth / 2
                        }
                    }
                ];

                axesLabels.forEach(
                    function(label) {
                        var geometry = new THREE.TextGeometry(label.text, {
                            font: font,
                            size: fontSize,
                            height: fontDepth,
                            curveSegments: 8
                        });
                        var material = new THREE.MeshBasicMaterial({
                            color: label.colour
                        });

                        var text = new THREE.Mesh(geometry, material);

                        text.position.set(
                            label.position.x,
                            label.position.y,
                            label.position.z
                        );
                        text.name = label.text;

                        visual.add(text);
                    }.bind(this)
                );
            }.bind(this)
        );

        visual.onBeforeRender = function(
            renderer,
            scene,
            camera,
            geometry,
            material,
            group
        ) {
            var distance = this._view.camera.near * 10;

            this.visual.scale.set(distance / 20, distance / 20, distance / 20);

            var aspectRatio =
                this._view.container.clientWidth /
                this._view.container.clientHeight;
            var verticalFov = (this._view.camera.fov * Math.PI) / 180;
            var horizontalFov =
                2 * Math.atan(Math.tan(verticalFov / 2) * aspectRatio);
            var width = 2 * Math.tan(horizontalFov / 2) * distance;
            var height = 2 * Math.tan(verticalFov / 2) * distance;

            this.visual.position.set(
                (-width / 2) * 0.85,
                (-height / 2) * 0.85,
                -distance
            );

            var rotation = rotateToWorld(
                this._view.camera,
                this._view.controls
            );
            this.visual.rotation.set(rotation.x, rotation.y, 0);
        }.bind(this);

        return visual;
    }

    fetch(route) {
        var loader = new THREE.FileLoader();
        loader.setResponseType('json');

        loader.load(
            route,
            function(json) {
                this.visual = this.create(json);

                this.cache[route] = this.visual;

                this._view.camera.add(this.visual);
            }.bind(this),
            loadingCallback.bind(this)
        );
    }
}

export { ViewAxesVisual };
