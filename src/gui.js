/**
 * @author Colour Developers / https://www.colour-science.org/
 */

// https://stackoverflow.com/a/45699568/931625
function updateDropdown(controls, attribute, dropdown, value, options) {
    if (options.constructor.name == 'Array') {
        var keys = options;
    } else if (options.constructor.name == 'Object') {
        var keys = Object.keys(options);
    }

    keys.sort();

    var innerHTML = '<select>\n';

    for (var i = 0; i < keys.length; i++) {
        innerHTML += `<option value="${keys[i]}">${keys[i]}</option>\n`;
    }

    innerHTML += '</select>';

    dropdown.domElement.children[0].innerHTML = innerHTML;
    dropdown.domElement.children[0].selectedIndex = keys.indexOf(value);
}

function dropdownOptions(dropdown) {
    dropdown = dropdown.domElement.children[0];
    var options = new Array();

    for (var i = 0; i < dropdown.options.length; i++) {
        options[i] = dropdown.options[i].value;
    }

    return options;
}

export { updateDropdown, dropdownOptions };
