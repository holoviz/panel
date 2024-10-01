function clone(node) {
  var new_element = node.cloneNode(true);
  node.parentNode.replaceChild(new_element, node);
  return new_element
}

function documentReady(callback) {
  if (document.readyState != "loading") callback();
  else document.addEventListener("DOMContentLoaded", callback);
}

let loaded = false

function setupMobileSidebarKeyboardHandlers() {
  if (loaded) {
    return
  }
  loaded = true

  // These are hidden checkboxes at the top of the page whose :checked property
  // allows the mobile sidebars to be hidden or revealed via CSS.
  const primaryToggle = document.getElementById("pst-primary-sidebar-checkbox");
  const secondaryToggle = document.getElementById(
    "pst-secondary-sidebar-checkbox",
  );
  const primarySidebar = document.querySelector(".bd-sidebar-primary");
  const secondarySidebar = document.querySelector(".bd-sidebar-secondary");

  // Toggle buttons -
  //
  // These are the hamburger-style buttons in the header nav bar. When the user
  // clicks, the button transmits the click to the hidden checkboxes used by the
  // CSS to control whether the sidebar is open or closed.
  const primaryClickTransmitter = document.querySelector(".primary-toggle");
  const secondaryClickTransmitter = document.querySelector(".secondary-toggle");
  [
    [primaryClickTransmitter, primaryToggle, primarySidebar],
    [secondaryClickTransmitter, secondaryToggle, secondarySidebar],
  ].forEach(([clickTransmitter, toggle, sidebar]) => {
    if (!clickTransmitter) {
      return;
    }
    const cloned = clone(clickTransmitter)
    cloned.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      toggle.checked = !toggle.checked;

      // If we are opening the sidebar, move focus to the first focusable item
      // in the sidebar
      if (toggle.checked) {
        // Note: this selector is not exhaustive, and we may need to update it
        // in the future
        const tabStop = sidebar.querySelector("a, button");
        // use setTimeout because you cannot move focus synchronously during a
        // click in the handler for the click event
        setTimeout(() => tabStop.focus(), 100);
      }
    });
  });

  // Escape key -
  //
  // When sidebar is open, user should be able to press escape key to close the
  // sidebar.
  [
    [primarySidebar, primaryToggle, primaryClickTransmitter],
    [secondarySidebar, secondaryToggle, secondaryClickTransmitter],
  ].forEach(([sidebar, toggle, transmitter]) => {
    if (!sidebar) {
      return;
    }
    sidebar.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        toggle.checked = false;
        transmitter.focus();
      }
    });
  });

  // When the <label> overlay is clicked to close the sidebar, return focus to
  // the opener button in the nav bar.
  [
    [primaryToggle, primaryClickTransmitter],
    [secondaryToggle, secondaryClickTransmitter],
  ].forEach(([toggle, transmitter]) => {
    toggle.addEventListener("change", (event) => {
      if (!event.currentTarget.checked) {
        transmitter.focus();
      }
    });
  });
}

documentReady(setupMobileSidebarKeyboardHandlers)
