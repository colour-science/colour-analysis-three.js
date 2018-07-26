import { removeObjectByName } from '../common.js';

class Visual {
    constructor(parent, settings) {
        this._parent = parent;

        this._name = settings.name || 'visual';
        this._visible = settings.visible || true;

        this._cache = {};

        this._visual = undefined;
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

    route() {
        throw Error('Method must be reimplemented in subclass!');
    }

    add() {
        if (this._parent != undefined) {
            removeObjectByName(this._parent, this._name);
        }

        var route = this.route();

        if (route in this._cache) {
            this._visual = this._cache[route];

            this._parent.add(this._visual);
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
                if (this._parent.parent != undefined){
                console.log(this._parent.parent.children);
            }
            }.bind(this)
        );
    }
}

export { Visual };
