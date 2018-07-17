import { Visual } from './visual.js';
import { fetchJSON, rotateToWorld } from '../common.js';

class ViewAxesVisual extends Visual {
    constructor(view, settings) {
        super(view.scene, { ...settings, ...{ name: 'view-axes-visual' } });

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

    add() {
        var route = this.route();

        if (route in this.cache) {
            this.visual = this.cache[route];

            this.view.camera.add(this.visual);
        } else {
            this.fetch(route);
        }
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

        visual.onBeforeRender = function(
            renderer,
            scene,
            camera,
            geometry,
            material,
            group
        ) {
            var distance = this._view.camera.near * 10;

            visual.scale.set(distance / 20, distance / 20, distance / 20);

            var aspectRatio =
                this._view.container.clientWidth /
                this._view.container.clientHeight;
            var verticalFov = (this._view.camera.fov * Math.PI) / 180;
            var horizontalFov =
                2 * Math.atan(Math.tan(verticalFov / 2) * aspectRatio);
            var width = 2 * Math.tan(horizontalFov / 2) * distance;
            var height = 2 * Math.tan(verticalFov / 2) * distance;

            visual.position.set(
                (-width / 2) * 0.9,
                (-height / 2) * 0.9,
                -distance
            );

            var rotation = rotateToWorld(
                this._view.camera,
                this._view.controls
            );
            visual.rotation.set(rotation.x, rotation.y, 0);
        }.bind(this);

        return visual;
    }

    fetch(route) {
        fetchJSON(
            route,
            function(json) {
                this.visual = this.create(json);

                this.cache[route] = this.visual;

                this.view.camera.add(this.visual);
            }.bind(this)
        );
    }
}

export { ViewAxesVisual };
