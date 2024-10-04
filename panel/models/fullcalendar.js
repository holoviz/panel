import { Calendar } from '@fullcalendar/core';

export function render({ model, el }) {
  function createCalendar(plugins) {
    let calendar = new Calendar(el, {
      businessHours: model.business_hours,
      buttonIcons: model.button_icons,
      buttonText: model.button_text,
      contentHeight: model.content_height,
      dateAlignment: model.date_alignment,
      dateIncrement: model.date_increment,
      events: model.value,
      expandRows: model.expand_rows,
      footerToolbar: model.footer_toolbar,
      handleWindowResize: model.handle_window_resize,
      headerToolbar: model.header_toolbar,
      initialDate: model.initial_date,
      initialView: model.initial_view,
      multiMonthMaxColumns: model.multi_month_max_columns,
      nowIndicator: model.now_indicator,
      plugins: plugins,
      showNonCurrentDates: model.show_non_current_dates,
      stickyFooterScrollbar: model.sticky_footer_scrollbar,
      stickyHeaderDates: model.sticky_header_dates,
      titleFormat: model.title_format,
      titleRangeSeparator: model.title_range_separator,
      validRange: model.valid_range,
      windowResizeDelay: model.window_resize_delay,
      datesSet: function (info) {
        model.send_msg({ 'current_date': calendar.getDate().toISOString() });
      },
    });

    if (model.aspect_ratio) {
      calendar.setOption('aspectRatio', model.aspect_ratio);
    }

    model.on("msg:custom", (event) => {
      if (event.type === 'next') {
        calendar.next();
      }
      else if (event.type === 'prev') {
        calendar.prev();
      }
      else if (event.type === 'prevYear') {
        calendar.prevYear();
      }
      else if (event.type === 'nextYear') {
        calendar.nextYear();
      }
      else if (event.type === 'today') {
        calendar.today();
      }
      else if (event.type === 'gotoDate') {
        calendar.gotoDate(event.date);
      }
      else if (event.type === 'incrementDate') {
        calendar.incrementDate(event.increment);
      }
      else if (event.type === 'updateSize') {
        calendar.updateSize();
      }
      else if (event.type === 'updateOption') {
        calendar.setOption(event.key, event.value);
      }
    });
    calendar.render();
  }

  let plugins = [];
  function loadPluginIfNeeded(viewName, pluginName) {
    if (model.initial_view.startsWith(viewName) ||
      (model.header_toolbar && Object.values(model.header_toolbar).some(v => v.includes(viewName))) ||
      (model.footer_toolbar && Object.values(model.footer_toolbar).some(v => v.includes(viewName)))) {
      return import(`@fullcalendar/${pluginName}`).then(plugin => {
        plugins.push(plugin.default);
        return plugin.default;
      });
    }
    return Promise.resolve(null);
  }

  Promise.all([
    loadPluginIfNeeded('dayGrid', 'daygrid'),
    loadPluginIfNeeded('timeGrid', 'timegrid'),
    loadPluginIfNeeded('list', 'list'),
    loadPluginIfNeeded('multiMonth', 'multimonth')
  ]).then(loadedPlugins => {
    const filteredPlugins = loadedPlugins.filter(plugin => plugin !== null);
    createCalendar(filteredPlugins);
  });
}