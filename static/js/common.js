function fetchJSON(url, callback) {
    return fetch(url)
        .then(function(response) {
            return response.json();
        })
        .then(function(json) {
            callback(json);
        })
        .catch(function(error) {
            console.error(error);
        });
}

function removeObjectByName(scene, name) {
    while (scene.getObjectByName(name) != undefined) {
        scene.remove(scene.getObjectByName(name));
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

export { fetchJSON, removeObjectByName, rotateToWorld };
