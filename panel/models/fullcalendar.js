import {Calendar} from "@fullcalendar/core"

export function render({model, el}) {
  function createCalendar(plugins, interactionPlugin = null) {
    const defaultPlugins = interactionPlugin ? [interactionPlugin] : []

    const calendar = new Calendar(el, {
      businessHours: model.business_hours,
      buttonIcons: model.button_icons,
      buttonText: model.button_text,
      contentHeight: model.content_height,
      dateIncrement: model.date_increment,
      events: model.value,
      expandRows: model.expand_rows,
      footerToolbar: model.footer_toolbar,
      handleWindowResize: model.handle_window_resize,
      headerToolbar: model.header_toolbar,
      initialView: model.current_view,
      navLinks: model.nav_links,
      nowIndicator: model.now_indicator,
      plugins: defaultPlugins.concat(plugins),
      showNonCurrentDates: model.show_non_current_dates,
      stickyFooterScrollbar: model.sticky_footer_scrollbar,
      stickyHeaderDates: model.sticky_header_dates,
      timeZone: model.time_zone,
      titleFormat: model.title_format,
      titleRangeSeparator: model.title_range_separator,
      validRange: model.valid_range,
      windowResizeDelay: model.window_resize_delay,
      ...(interactionPlugin && {
        droppable: model.droppable,
        editable: model.editable,
        eventDurationEditable: model.event_duration_editable,
        eventResizableFromStart: model.event_resizable_from_start,
        eventResourceEditable: model.event_resource_editable,
        eventStartEditable: model.event_start_editable,
        selectable: model.selectable,
        selectMirror: model.select_mirror,
        unselectAuto: model.unselect_auto,
        unselectCancel: model.unselect_cancel,
        selectAllow: model.select_allow,
        selectMinDistance: model.select_min_distance,
        dateClick(info) {
          model.send_msg({date_click: JSON.stringify(info)})
        },
        drop(info) {
          model.send_msg({drop: JSON.stringify(info)})
        },
        eventDragStart(info) {
          model.send_msg({event_drag_start: JSON.stringify(info)})
        },
        eventDragStop(info) {
          model.send_msg({event_drag_stop: JSON.stringify(info)})
        },
        eventDrop(info) {
          model.send_msg({event_drop: JSON.stringify(info)})
        },
        eventLeave(info) {
          model.send_msg({event_leave: JSON.stringify(info)})
        },
        eventReceive(info) {
          model.send_msg({event_receive: JSON.stringify(info)})
        },
        eventResize(info) {
          model.send_msg({event_resize: JSON.stringify(info)})
        },
        eventResizeStart(info) {
          model.send_msg({event_resize_start: JSON.stringify(info)})
        },
        eventResizeStop(info) {
          model.send_msg({event_resize_stop: JSON.stringify(info)})
        },
        select(info) {
          model.send_msg({select: JSON.stringify(info)})
        },
        unselect(info) {
          model.send_msg({unselect: JSON.stringify(info)})
        },

      }),
      datesSet(info) {
        model.send_msg({current_date: calendar.getDate().toISOString()})
      },
      viewClassNames(info) {
        model.send_msg({current_view: info.view.type})
      },
      navLinkDayClick(date, jsEvent) {
        calendar.changeView("timeGridDay", date)
      },
      navLinkWeekClick(weekStart, jsEvent) {
      },
    })

    if (model.current_date) {
      calendar.gotoDate(model.current_date)
    }

    if (model.dateAlignment) {
      calendar.setOption("dateAlignment", model.dateAlignment)
    }

    if (model.current_view == "multiMonth") {
      calendar.setOption("multiMonthMaxColumns", model.multi_month_max_columns)
    }

    if (model.aspect_ratio) {
      calendar.setOption("aspectRatio", model.aspect_ratio)
    }

    model.on("msg:custom", (event) => {
      if (event.type === "next") {
        calendar.next()
      } else if (event.type === "prev") {
        calendar.prev()
      } else if (event.type === "prevYear") {
        calendar.prevYear()
      } else if (event.type === "nextYear") {
        calendar.nextYear()
      } else if (event.type === "today") {
        calendar.today()
      } else if (event.type === "gotoDate") {
        calendar.gotoDate(event.date)
      } else if (event.type === "incrementDate") {
        calendar.incrementDate(event.increment)
      } else if (event.type === "updateOption") {
        calendar.setOption(event.key, event.value)
      } else if (event.type === "changeView") {
        calendar.changeView(event.view, event.date)
      }
    })
    calendar.render()
  }

  const plugins = []
  function loadPluginIfNeeded(viewName, pluginName) {
    if (model.current_view.startsWith(viewName) ||
      (model.header_toolbar && Object.values(model.header_toolbar).some(v => v.includes(viewName))) ||
      (model.footer_toolbar && Object.values(model.footer_toolbar).some(v => v.includes(viewName)))) {
      return import(`@fullcalendar/${pluginName}`).then(plugin => {
        plugins.push(plugin.default)
        return plugin.default
      })
    }
    return Promise.resolve(null)
  }

  const pluginPromises = [
    loadPluginIfNeeded("dayGrid", "daygrid"),
    loadPluginIfNeeded("timeGrid", "timegrid"),
    loadPluginIfNeeded("list", "list"),
    loadPluginIfNeeded("multiMonth", "multimonth"),
  ]

  const interactionPromise = (model.selectable || model.editable)
    ? import("@fullcalendar/interaction").then(module => module.default)
    : Promise.resolve(null)

  Promise.all([...pluginPromises, interactionPromise])
    .then(([interactionPlugin, ...loadedPlugins]) => {
      const filteredPlugins = loadedPlugins.filter(plugin => plugin !== null)
      createCalendar(filteredPlugins, interactionPlugin)
    })
}
