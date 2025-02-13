export const TREE_DATA = [
  {
    label: '深圳总部',
    value: 0,
    children: [
      {
        label: '总办',
        value: '0-0',
      },
      {
        label: '市场部',
        value: '0-1',
        children: [
          {
            label: '采购1组',
            value: '0-1-0',
          },
          {
            label: '采购2组',
            value: '0-1-1',
          },
        ],
      },
      {
        label: '技术部',
        value: '0-2',
      },
    ],
  },
  {
    label: '北京总部',
    value: 1,
    children: [
      {
        label: '总办',
        value: '1-0',
      },
      {
        label: '市场部',
        value: '1-1',
        children: [
          {
            label: '采购1组',
            value: '1-1-0',
          },
          {
            label: '采购2组',
            value: '1-1-1',
          },
        ],
      },
    ],
  },
  {
    label: '上海总部',
    value: 2,
    children: [
      {
        label: '市场部',
        value: '2-0',
      },
      {
        label: '财务部',
        value: '2-1',
        children: [
          {
            label: '财务1组',
            value: '2-1-0',
          },
          {
            label: '财务2组',
            value: '2-1-1',
          },
        ],
      },
    ],
  },
  {
    label: '湖南',
    value: 3,
  },
  {
    label: '湖北',
    value: 4,
  },
];
