import { removeObjectByName, loadingCallback } from '../common.js';

/**
 * @author Colour Developers / https://www.colour-science.org/
 */

class Visual {
    constructor(parent, settings) {
        this._parent = parent;

        this._name = settings.name || 'visual';
        this._visible = settings.visible || true;
        this._loadingCallback = settings.loadingCallback || loadingCallback;

        this._cache = {};

        this._visual = undefined;

        this._loading = false;
    }

    get parent() {
        return this._parent;
    }

    set parent(value) {
        if (this._parent != undefined) {
            removeObjectByName(this._parent, this._name);
        }
        this._parent = value;
        if (this._visual != undefined) {
            this._parent.add(this._visual);
        }
    }

    get name() {
        return this._name;
    }

    set name(value) {
        throw new Error('"name" property is read only!');
    }

    get visible() {
        return this._visible;
    }

    set visible(value) {
        this._visible = value;
        Object.keys(this._cache).forEach(
            function(key) {
                this._cache[key].visible = value;
            }.bind(this)
        );
    }
    get loadingCallback() {
        return this._loadingCallback;
    }

    set loadingCallback(value) {
        this._loadingCallback = value;
    }

    get cache() {
        return this._cache;
    }

    set cache(value) {
        throw new Error('"cache" property is read only!');
    }

    get visual() {
        return this._visual;
    }

    set visual(value) {
        if (this._parent != undefined) {
            removeObjectByName(this._parent, this._name);
        }
        this._visual = value;
        if (this._visual != undefined) {
            this._parent.add(this._visual);
        }
    }

    get loading() {
        return this._loading;
    }

    set loading(value) {
        throw new Error('"cache" property is read only!');
    }

    route() {
        throw Error('Method must be reimplemented in subclass!');
    }

    add() {
        if (this._parent != undefined) {
            removeObjectByName(this._parent, this._name);
        }

        var route = this.route();

        this._loading = true;

        if (route in this._cache) {
            this._visual = this._cache[route];

            this._parent.add(this._visual);

            this._loading = false;
        } else {
            this.fetch(route);
        }
    }

    create(geometry) {
        throw Error('Method must be reimplemented in subclass!');
    }

    fetch(route) {
        var loader = new THREE.BufferGeometryLoader();

        loader.load(
            route,
            function(geometry, materials) {
                this._visual = this.create(geometry);

                this._cache[route] = this._visual;

                this._parent.add(this._visual);

                this._loading = false;
            }.bind(this),

            this._loadingCallback.bind(this)
        );
    }
}

export { Visual };
