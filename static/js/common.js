function removeObjectByName(scene, name) {
    while (scene.getObjectByName(name) != undefined) {
        var object = scene.getObjectByName(name);
        object.parent.remove(object);
    }
}

// https://stackoverflow.com/a/49389874/931625
function rotateToWorld(camera, controls) {
    var position = new THREE.Vector3();
    var target = new THREE.Vector3();

    position.copy(camera.position);
    target.copy(controls.target);

    position.sub(target);

    var distanceXyz = Math.sqrt(
        position.x * position.x +
            position.y * position.y +
            position.z * position.z
    );
    var distanceXz = Math.sqrt(
        position.x * position.x + position.z * position.z
    );

    return {
        x: Math.acos(distanceXz / distanceXyz) * (position.y > 0 ? 1 : -1),
        y: Math.acos(position.z / distanceXz) * (position.x > 0 ? -1 : 1),
        z: 0
    };
}

function loadingCallback(xhr) {
    var loaded = Math.round(
        (xhr.loaded /
            parseFloat(xhr.target.getResponseHeader('x-content-length'))) *
            100
    );
    document.getElementById('logging').innerText = `${
        this.name
    }: ${loaded}% loaded...`;
}

export { removeObjectByName, rotateToWorld, loadingCallback };
