import { ChartType, Plugin } from 'chart.js';

declare module 'chartjs-plugin-zoom' {
  interface ZoomPluginOptions {
    zoom: {
      wheel: {
        enabled: boolean;
      };
      pinch: {
        enabled: boolean;
      };
      mode: string;
    };
    pan: {
      enabled: boolean;
      mode: string;
    };
  }

  const zoomPlugin: Plugin<ChartType>;
  export default zoomPlugin;
}

declare module 'chart.js' {
  interface PluginOptionsByType<TType extends ChartType> {
    zoom: ZoomPluginOptions;
  }
} 