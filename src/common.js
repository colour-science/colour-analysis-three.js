function serverRoute(route) {
    if (window.colourAnalysisServer != undefined) {
        return `${window.colourAnalysisServer}${route}`;
    } else {
        return route;
    }
}

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
function fadeElement(element, registry, delay, speed) {
    var delay = delay || 5000;
    var speed = speed || 10;

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

function message(text, element, registry, delay, speed) {
    if (element == null || element == undefined) {
        return;
    }

    element.innerText = text;
    clearRegistry(element, registry);
    fadeElement(element, registry, delay, speed);
}

window.info_id_registry = new Array();

function info(text, delay, speed) {
    message(
        text,
        document.getElementById('info'),
        window.info_id_registry,
        delay,
        speed
    );
}

window.warning_id_registry = new Array();

function warning(text, delay, speed) {
    message(
        text,
        document.getElementById('warning'),
        window.warning_id_registry,
        delay,
        speed
    );
}

function loadingCallback(xhr) {
    var loaded = Math.round(
        (xhr.loaded /
            parseFloat(xhr.target.getResponseHeader('x-content-length'))) *
            100
    );

    info(`${this.name}: ${loaded}% loaded...`);
}

export {
    serverRoute,
    removeObjectByName,
    rotateToWorld,
    fadeElement,
    message,
    info,
    warning,
    loadingCallback
};
