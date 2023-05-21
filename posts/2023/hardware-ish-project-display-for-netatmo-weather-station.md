I've finally [published](https://github.com/vrusinov/co2_monitors/tree/main/netatmo_esphome_m5stickc_display) a small project: ESPHome-powered display for the [Netatmo weather station](https://www.netatmo.com/en-gb/weather/weatherstation).

![Netatmo CO2 monitor](/posts/2023/netatmo_co2_monitor.jpg)

This is ESPHome-based display for Netatmo weather station. The primary goal is to display indoors CO2 concerntation in my home office so that I know when to open a window. Or when to close and hopefully save some money on heating.

The device itself is not a CO2 monitor and requires Netatmo to be working with HomeAssistant.

<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>

<pre class="mermaid">
graph LR
    subgraph Internet
        NC([netatmo.com])
    end
    subgraph Home
        Netatmo[(Netatmo Weather Station fa:fa-cloud)]
        HomeAssistant[HomeAssistant fa:fa-house]
        Display[CO2 Display fa:fa-display]
    end

    click Netatmo https://www.netatmo.com/en-gb/weather/weatherstation
    click NC https://my.netatmo.com/
    click HomeAssistant https://www.home-assistant.io/

    Netatmo-->Internet
    Internet-->HomeAssistant
    HomeAssistant-- Wi-Fi -->Display
</pre>

Find it here: [https://github.com/vrusinov/co2_monitors/tree/main/netatmo_esphome_m5stickc_display](https://github.com/vrusinov/co2_monitors/tree/main/netatmo_esphome_m5stickc_display)
