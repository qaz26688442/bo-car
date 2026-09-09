// Google Ads: initialize before the async Google tag finishes loading.
window.dataLayer = window.dataLayer || [];
window.gtag = function () { window.dataLayer.push(arguments); };
window.gtag('js', new Date());
window.gtag('config', 'AW-11045528501');
window.gtag('event', 'conversion', {
  send_to: 'AW-11045528501/j6F-CI6im4UYELXH9ZIp'
});

// Delegation covers header, hero, contact, mobile bar and 404 links.
// Keep native navigation, including LINE's new tab, even if tracking is blocked.
document.addEventListener('click', function (event) {
  const link = event.target.closest('a[href]');
  if (!link) return;

  const url = new URL(link.href, window.location.href);
  let sendTo;
  if (url.protocol === 'tel:') {
    sendTo = 'AW-11045528501/ATWTCKWT64kYELXH9ZIp';
  } else if (url.protocol === 'https:' &&
      (url.hostname === 'lin.ee' || url.hostname === 'line.me')) {
    sendTo = 'AW-11045528501/xH8sCKKT64kYELXH9ZIp';
  }

  if (sendTo) window.gtag('event', 'conversion', { send_to: sendTo });
});
