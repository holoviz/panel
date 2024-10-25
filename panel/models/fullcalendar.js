import {Calendar} from "@fullcalendar/core"

export function render({model, el}) {
  function createCalendar(plugins, interactionPlugin = null) {
    const defaultPlugins = interactionPlugin ? [interactionPlugin] : []

    const calendarConfig = {
      allDayMaintainDuration: model.all_day_maintain_duration,
      businessHours: model.business_hours,
      buttonIcons: model.button_icons,
      buttonText: model.button_text,
      contentHeight: model.content_height,
      dateIncrement: model.date_increment,
      dayMaxEventRows: model.day_max_event_rows,
      dayMaxEvents: model.day_max_events,
      displayEventEnd: model.display_event_end,
      displayEventTime: model.display_event_time,
      dragRevertDuration: model.drag_revert_duration,
      dragScroll: model.drag_scroll,
      editable: model.editable,
      eventBackgroundColor: model.event_background_color,
      eventBorderColor: model.event_border_color,
      eventColor: model.event_color,
      eventDisplay: model.event_display,
      eventDragMinDistance: model.event_drag_min_distance,
      eventDurationEditable: model.event_duration_editable,
      eventMaxStack: model.event_max_stack,
      eventOrder: model.event_order,
      eventOrderStrict: model.event_order_strict,
      eventResizableFromStart: model.event_resizable_from_start,
      eventStartEditable: model.event_start_editable,
      eventTextColor: model.event_text_color,
      events: model.value,
      expandRows: model.expand_rows,
      footerToolbar: model.footer_toolbar,
      handleWindowResize: model.handle_window_resize,
      headerToolbar: model.header_toolbar,
      initialView: model.current_view,
      moreLinkClick: model.more_link_click,
      navLinks: model.nav_links,
      nextDayThreshold: model.next_day_threshold,
      nowIndicator: model.now_indicator,
      plugins: defaultPlugins.concat(plugins),
      progressiveEventRendering: model.progressive_event_rendering,
      selectAllow: model.select_allow,
      selectMinDistance: model.select_min_distance,
      selectMirror: model.select_mirror,
      selectable: model.selectable,
      showNonCurrentDates: model.show_non_current_dates,
      snapDuration: model.snap_duration,
      stickyFooterScrollbar: model.sticky_footer_scrollbar,
      stickyHeaderDates: model.sticky_header_dates,
      timeZone: model.time_zone,
      titleRangeSeparator: model.title_range_separator,
      unselectAuto: model.unselect_auto,
      unselectCancel: model.unselect_cancel,
      validRange: model.valid_range,
      windowResizeDelay: model.window_resize_delay,
      datesSet(info) {
        model.send_msg({current_date: calendar.getDate().toISOString()})
      },
      eventClick(info) {
        model.send_msg({event_click: JSON.stringify(info)})
      },
      viewClassNames(info) {
        model.send_msg({current_view: info.view.type})
      },
      navLinkDayClick(date, jsEvent) {
        calendar.changeView("timeGridDay", date)
      },
      navLinkWeekClick(weekStart, jsEvent) {
        calendar.changeView("timeGridWeek", weekStart)
      },
    }

    if (model.editable || model.selectable) {
      Object.assign(calendarConfig, {
        editable: model.editable,
        selectable: model.selectable,
        dateClick(info) {
          model.send_msg({date_click: JSON.stringify(info)})
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
      })
    }

    const calendar = new Calendar(el, calendarConfig)

    if (model.current_date) {
      calendar.gotoDate(model.current_date)
    }

    if (model.dateAlignment) {
      calendar.setOption("dateAlignment", model.dateAlignment)
    }
    if (model.day_popover_format) {
      calendar.setOption("dayPopoverFormat", model.day_popover_format)
    }

    if (model.event_time_format) {
      calendar.setOption("eventTimeFormat", model.event_time_format)
    }

    if (model.title_format) {
      calendar.setOption("titleFormat", model.title_format)
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
      } else if (event.type === "scrollToTime") {
        calendar.scrollToTime(event.time)
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
