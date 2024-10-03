import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';

export function render({ model, el }) {
  let calendar = new Calendar(el, {
    plugins: [dayGridPlugin, timeGridPlugin],

    initialView: model.initial_view,
    events: model.value,
  });

  calendar.render();
}
