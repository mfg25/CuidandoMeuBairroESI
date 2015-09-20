import router from '../store/router'

// Convert number to locale string
export function format(number, opts) {
    return number.toLocaleString(router.getParam('lang'), opts)
}

// Convert number to locale string with 2 decimal digits
export function formatCur(number) {
    return format(number, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2}
    )
}

// Capitalize first letter
export function capitalize(string) {
    return string[0].toUpperCase() + string.slice(1)
}


// Runs a function when an element outside of node is clicked
// Clears the callback if no node is passed
// Ignore event if is ignoreEvent (usefull to ignore a initial event originated
// outside of node).
export function onClickedOutside(node, func, ignoreEvent) {
    if (node) {
        document.onclick = (event) => {
            // Clicked outside of the node
            if (event != ignoreEvent && !node.contains(event.target)) {
                console.log('OUT')
                func()
                document.onclick = undefined
            }
        }
    } else {
        document.onclick = undefined
    }
}
