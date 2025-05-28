function updateURLParameter(url, param, paramVal) {
  var TheAnchor = null
  var newAdditionalURL = ''
  var tempArray = url.split('?')
  var baseURL = tempArray[0]
  var additionalURL = tempArray[1]
  var temp = ''

  if (additionalURL) {
    var tmpAnchor = additionalURL.split('#')
    var TheParams = tmpAnchor[0]
    var TheAnchor = tmpAnchor[1]
    if (TheAnchor) {
      additionalURL = TheParams
    }
    tempArray = additionalURL.split('&')

    for (var i = 0; i < tempArray.length; i++) {
      if (tempArray[i].split('=')[0] != param) {
        newAdditionalURL += temp + tempArray[i]
        temp = '&'
      }
    }
  } else {
    var tmpAnchor = baseURL.split('#')
    var TheParams = tmpAnchor[0]
    var TheAnchor = tmpAnchor[1]
    if (TheParams) {
      baseURL = TheParams
    }
  }
  if (TheAnchor) {
    paramVal += '#' + TheAnchor
  }
  var rows_txt = temp + '' + param + '=' + paramVal
  return baseURL + '?' + newAdditionalURL + rows_txt
}

function toggleLightDarkTheme(theme) {
  var href = window.location.href
  if (theme === 'default') {
    theme = 'dark'
  } else {
    theme = 'default'
  }

  href = updateURLParameter(href, 'theme', theme)
  window.location.href = href
}

function changeLocation(href) {
  var href_old = window.location.href
  var url_old = new URL(href_old)
  var theme = url_old.searchParams.get('theme', '')
  if (theme) {
    href = updateURLParameter(href, 'theme', theme)
  }
  window.location.href = href
}

function isFullScreen() {
  return (
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  )
}

function exitFullScreen() {
  if (document.exitFullscreen) {
    document.exitFullscreen()
  } else if (document.mozCancelFullScreen) {
    document.mozCancelFullScreen()
  } else if (document.webkitExitFullscreen) {
    document.webkitExitFullscreen()
  } else if (document.msExitFullscreen) {
    document.msExitFullscreen()
  }
}

function requestFullScreen(element) {
  if (element.requestFullscreen) {
    element.requestFullscreen()
  } else if (element.mozRequestFullScreen) {
    element.mozRequestFullScreen()
  } else if (element.webkitRequestFullscreen) {
    element.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT)
  } else if (element.msRequestFullscreen) {
    element.msRequestFullscreen()
  }
}

function toggleFullScreen(caller) {
  if (isFullScreen()) {
    exitFullScreen()
  } else {
    requestFullScreen(caller.parentElement)
  }
}

function addFullScreenToggle() {
  const elements = document.getElementsByClassName('fullscreen-button')
  for (let element of elements) {
    element.setAttribute('onclick', 'toggleFullScreen(this)')
  }
}
document.addEventListener('fullscreenchange', function (e) {
  const button = e.target.getElementsByClassName('fullscreen-button')[0]
  if (isFullScreen()) {
    button.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 18 18"><path d="M3 12.5h2.5V15H7v-4H3v1.5zm2.5-7H3V7h4V3H5.5v2.5zM11 15h1.5v-2.5H15V11h-4v4zm1.5-9.5V3H11v4h4V5.5h-2.5z"/></svg>'
  } else {
    button.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 18 18"><path d="M4.5 11H3v4h4v-1.5H4.5V11zM3 7h1.5V4.5H7V3H3v4zm10.5 6.5H11V15h4v-4h-1.5v2.5zM11 3v1.5h2.5V7H15V3h-4z"/></svg>'
  }
})
