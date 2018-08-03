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

// https://stackoverflow.com/a/31658023/931625
function fadeElement(element, registry, speed, delay) {
    var speed = 10 || speed;
    var delay = 5000 || delay;

    registry.push(
        setTimeout(function() {
            element.style.opacity = 1;
            var timerId = setInterval(function() {
                var opacity = element.style.opacity;
                if (opacity == 0) {
                    clearInterval(timerId);
                } else {
                    element.style.opacity = opacity - 0.01;
                }
            }, speed);
            registry.push(timerId);
        }, delay)
    );
}

function clearRegistry(element, registry) {
    element.style.opacity = 1;
    while (registry.length > 0) {
        var id = registry.shift();
        window.clearInterval(id);
        window.clearTimeout(id);
    }
}

window.messages_registry = new Array();

function message(message) {
    var element = document.getElementById('message');
    element.innerText = message;
    clearRegistry(element, window.messages_registry);
    fadeElement(element, window.messages_registry);
}

window.alerts_registry = new Array();

function alert(message) {
    var element = document.getElementById('alert');
    element.innerText = message;
    clearRegistry(element, window.alerts_registry);
    fadeElement(element, window.alerts_registry);
}

function loadingCallback(xhr) {
    var loaded = Math.round(
        (xhr.loaded /
            parseFloat(xhr.target.getResponseHeader('x-content-length'))) *
            100
    );

    message(`${this.name}: ${loaded}% loaded...`);
}

export {
    removeObjectByName,
    rotateToWorld,
    fadeElement,
    message,
    alert,
    loadingCallback
};
