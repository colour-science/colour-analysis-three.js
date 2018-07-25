// https://stackoverflow.com/a/45699568/931625
function updateDropdown(controls, attribute, dropdown, value, options) {
    if (options.constructor.name == 'Array') {
        var keys = options;
    } else if (options.constructor.name == 'Object') {
        var keys = Object.keys(options);
    }

    keys.sort();

    controls[attribute] = keys;

    var innerHTML = '<select>\n';

    for (var i = 0; i < keys.length; i++) {
        innerHTML += `<option value="${keys[i]}">${keys[i]}</option>\n`;
    }

    innerHTML += '</select>';

    dropdown.domElement.children[0].innerHTML = innerHTML;
    dropdown.domElement.children[0].selectedIndex = keys.indexOf(value);
}

export { updateDropdown };
