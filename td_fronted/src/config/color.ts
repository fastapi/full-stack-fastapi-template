export type TColorToken = Record<string, string>;
export type TColorSeries = Record<string, TColorToken>;

// TODO: 中性色暂时固定 待tvision-color生成带色彩倾向的中性色
export const LIGHT_CHART_COLORS = {
  textColor: 'rgba(0, 0, 0, 0.9)',
  placeholderColor: 'rgba(0, 0, 0, 0.35)',
  borderColor: '#dcdcdc',
  containerColor: '#fff',
};

export const DARK_CHART_COLORS = {
  textColor: 'rgba(255, 255, 255, 0.9)',
  placeholderColor: 'rgba(255, 255, 255, 0.35)',
  borderColor: '#5e5e5e',
  containerColor: '#242424',
};

export type TChartColor = typeof LIGHT_CHART_COLORS;

export const DEFAULT_COLOR_OPTIONS = [
  '#0052D9',
  '#0594FA',
  '#00A870',
  '#EBB105',
  '#ED7B2F',
  '#E34D59',
  '#ED49B4',
  '#834EC2',
];
