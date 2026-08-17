export default `progress{appearance:none;-moz-appearance:none;-webkit-appearance:none;border:none;height:20px;border-radius:3px;box-shadow:0 2px 3px rgba(0, 0, 0, 0.5) inset;color:royalblue;position:relative;margin:0 0 1.5em;width:100%;}progress[value]::-webkit-progress-bar{background-color:whiteSmoke;border-radius:3px;box-shadow:0 2px 3px rgba(0, 0, 0, 0.5) inset;}progress[value] ::-webkit-progress-value{position:relative;background-size:35px 20px,
    100% 100%,
    100% 100%;border-radius:3px;}progress.active:not([value])::before{background-position:10%;animation-name:stripes;animation-duration:3s;animation-timing-function:linear;animation-iteration-count:infinite;}progress[value]::-moz-progress-bar{background-size:35px 20px,
    100% 100%,
    100% 100%;border-radius:3px;}progress:not([value])::-moz-progress-bar{border-radius:3px;background:linear-gradient(
      -45deg,
      transparent 33%,
      rgba(0, 0, 0, 0.2) 33%,
      rgba(0, 0, 0, 0.2) 66%,
      transparent 66%
    )
    left/2.5em 1.5em;}progress.active:not([value])::-moz-progress-bar{background-position:10%;animation-name:stripes;animation-duration:3s;animation-timing-function:linear;animation-iteration-count:infinite;}progress.active:not([value])::-webkit-progress-bar{background-position:10%;animation-name:stripes;animation-duration:3s;animation-timing-function:linear;animation-iteration-count:infinite;}progress.primary[value]::-webkit-progress-value{background-color:var(--primary-bg-color);}progress.primary:not([value])::before{background-color:var(--primary-bg-color);}progress.primary:not([value])::-webkit-progress-bar{background-color:var(--primary-bg-color);}progress.primary::-moz-progress-bar{background-color:var(--primary-bg-color);}progress.secondary[value]::-webkit-progress-value{background-color:var(--secondary-bg-color);}progress.secondary:not([value])::before{background-color:var(--secondary-bg-color);}progress.secondary:not([value])::-webkit-progress-bar{background-color:var(--secondary-bg-color);}progress.secondary::-moz-progress-bar{background-color:var(--secondary-bg-color);}progress.success[value]::-webkit-progress-value{background-color:var(--success-bg-color);}progress.success:not([value])::before{background-color:var(--success-bg-color);}progress.success:not([value])::-webkit-progress-bar{background-color:var(--success-bg-color);}progress.success::-moz-progress-bar{background-color:var(--success-bg-color);}progress.danger[value]::-webkit-progress-value{background-color:var(--danger-bg-color);}progress.danger:not([value])::before{background-color:var(--danger-bg-color);}progress.danger:not([value])::-webkit-progress-bar{background-color:var(--danger-bg-color);}progress.danger::-moz-progress-bar{background-color:var(--danger-bg-color);}progress.warning[value]::-webkit-progress-value{background-color:var(--warning-bg-color);}progress.warning:not([value])::before{background-color:var(--warning-bg-color);}progress.warning:not([value])::-webkit-progress-bar{background-color:var(--warning-bg-color);}progress.warning::-moz-progress-bar{background-color:var(--warning-bg-color);}progress.info[value]::-webkit-progress-value{background-color:var(--info-bg-color);}progress.info:not([value])::before{background-color:var(--info-bg-color);}progress.info:not([value])::-webkit-progress-bar{background-color:var(--info-bg-color);}progress.info::-moz-progress-bar{background-color:var(--info-bg-color);}progress.light[value]::-webkit-progress-value{background-color:var(--light-bg-color);}progress.light:not([value])::before{background-color:var(--light-bg-color);}progress.light:not([value])::-webkit-progress-bar{background-color:var(--light-bg-color);}progress.light::-moz-progress-bar{background-color:var(--light-bg-color);}progress.dark[value]::-webkit-progress-value{background-color:var(--dark-bg-color);}progress.dark:not([value])::-webkit-progress-bar{background-color:var(--dark-bg-color);}progress.dark:not([value])::before{background-color:var(--dark-bg-color);}progress.dark::-moz-progress-bar{background-color:var(--dark-bg-color);}progress:not([value])::-webkit-progress-bar{border-radius:3px;background:linear-gradient(
      -45deg,
      transparent 33%,
      rgba(0, 0, 0, 0.2) 33%,
      rgba(0, 0, 0, 0.2) 66%,
      transparent 66%
    )
    left/2.5em 1.5em;}progress:not([value])::before{content:' ';position:absolute;height:20px;top:0;left:0;right:0;bottom:0;border-radius:3px;background:linear-gradient(
      -45deg,
      transparent 33%,
      rgba(0, 0, 0, 0.2) 33%,
      rgba(0, 0, 0, 0.2) 66%,
      transparent 66%
    )
    left/2.5em 1.5em;}@keyframes stripes{from{background-position:0%;}to{background-position:100%;}}`
