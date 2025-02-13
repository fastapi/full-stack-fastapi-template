import axios, {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosRequestHeaders,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios';
import cloneDeep from 'lodash/cloneDeep';
import debounce from 'lodash/debounce';
import isFunction from 'lodash/isFunction';
import throttle from 'lodash/throttle';
import { stringify } from 'qs';

import { ContentTypeEnum } from '@/constants';
import { AxiosRequestConfigRetry, RequestOptions, Result } from '@/types/axios';

import { AxiosCanceler } from './AxiosCancel';
import { CreateAxiosOptions } from './AxiosTransform';

/**
 * Axios 模块
 */
export class VAxios {
  /**
   * Axios实例句柄
   * @private
   */
  private instance: AxiosInstance;

  /**
   * Axios配置
   * @private
   */
  private readonly options: CreateAxiosOptions;

  constructor(options: CreateAxiosOptions) {
    this.options = options;
    this.instance = axios.create(options);
    this.setupInterceptors();
  }

  /**
   * 创建Axios实例
   * @param config
   * @private
   */
  private createAxios(config: CreateAxiosOptions): void {
    this.instance = axios.create(config);
  }

  /**
   * 获取数据处理类
   * @private
   */
  private getTransform() {
    const { transform } = this.options;
    return transform;
  }

  /**
   * 获取Axios实例
   */
  getAxios(): AxiosInstance {
    return this.instance;
  }

  /**
   * 配置Axios
   * @param config
   */
  configAxios(config: CreateAxiosOptions) {
    if (!this.instance) return;
    this.createAxios(config);
  }

  /**
   * 设置公共头部信息
   * @param headers
   */
  setHeader(headers: Record<string, string>): void {
    if (!this.instance) return;
    Object.assign(this.instance.defaults.headers, headers);
  }

  /**
   * 设置拦截器
   * @private
   */
  private setupInterceptors() {
    const transform = this.getTransform();
    if (!transform) return;

    const { requestInterceptors, requestInterceptorsCatch, responseInterceptors, responseInterceptorsCatch } =
      transform;
    const axiosCanceler = new AxiosCanceler();

    // 请求拦截器
    this.instance.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      // 如果忽略取消令牌，则不会取消重复的请求
      // @ts-ignore
      const { ignoreCancelToken } = config.requestOptions;
      const ignoreCancel = ignoreCancelToken ?? this.options.requestOptions?.ignoreCancelToken;
      if (!ignoreCancel) axiosCanceler.addPending(config);

      if (requestInterceptors && isFunction(requestInterceptors)) {
        config = requestInterceptors(config, this.options) as InternalAxiosRequestConfig;
      }

      return config;
    }, undefined);

    // 请求错误处理
    if (requestInterceptorsCatch && isFunction(requestInterceptorsCatch)) {
      this.instance.interceptors.request.use(undefined, requestInterceptorsCatch);
    }

    // 响应结果处理
    this.instance.interceptors.response.use((res: AxiosResponse) => {
      if (res) axiosCanceler.removePending(res.config);
      if (responseInterceptors && isFunction(responseInterceptors)) {
        res = responseInterceptors(res);
      }
      return res;
    }, undefined);

    // 响应错误处理
    if (responseInterceptorsCatch && isFunction(responseInterceptorsCatch)) {
      this.instance.interceptors.response.use(undefined, (error) => responseInterceptorsCatch(error, this.instance));
    }
  }

  /**
   * 支持 FormData 请求格式
   * @param config
   */
  supportFormData(config: AxiosRequestConfig) {
    const headers = config.headers || (this.options.headers as AxiosRequestHeaders);
    const contentType = headers?.['Content-Type'] || headers?.['content-type'];

    if (
      contentType !== ContentTypeEnum.FormURLEncoded ||
      !Reflect.has(config, 'data') ||
      config.method?.toUpperCase() === 'GET'
    ) {
      return config;
    }

    return {
      ...config,
      data: stringify(config.data, { arrayFormat: 'brackets' }),
    };
  }

  /**
   * 支持 params 序列化
   * @param config
   */
  supportParamsStringify(config: AxiosRequestConfig) {
    const headers = config.headers || this.options.headers;
    const contentType = headers?.['Content-Type'] || headers?.['content-type'];

    if (contentType === ContentTypeEnum.FormURLEncoded || !Reflect.has(config, 'params')) {
      return config;
    }

    return {
      ...config,
      paramsSerializer: (params: any) => stringify(params, { arrayFormat: 'brackets' }),
    };
  }

  get<T = any>(config: AxiosRequestConfig, options?: RequestOptions): Promise<T> {
    return this.request({ ...config, method: 'GET' }, options);
  }

  post<T = any>(config: AxiosRequestConfig, options?: RequestOptions): Promise<T> {
    return this.request({ ...config, method: 'POST' }, options);
  }

  put<T = any>(config: AxiosRequestConfig, options?: RequestOptions): Promise<T> {
    return this.request({ ...config, method: 'PUT' }, options);
  }

  delete<T = any>(config: AxiosRequestConfig, options?: RequestOptions): Promise<T> {
    return this.request({ ...config, method: 'DELETE' }, options);
  }

  patch<T = any>(config: AxiosRequestConfig, options?: RequestOptions): Promise<T> {
    return this.request({ ...config, method: 'PATCH' }, options);
  }

  /**
   * 上传文件封装
   * @param key 文件所属的key
   * @param file 文件
   * @param config 请求配置
   * @param options
   */
  upload<T = any>(key: string, file: File, config: AxiosRequestConfig, options?: RequestOptions): Promise<T> {
    const params: FormData = config.params ?? new FormData();
    params.append(key, file);

    return this.request(
      {
        ...config,
        method: 'POST',
        headers: {
          'Content-Type': ContentTypeEnum.FormData,
        },
        params,
      },
      options,
    );
  }

  /**
   * 请求封装
   * @param config
   * @param options
   */
  request<T = any>(config: AxiosRequestConfigRetry, options?: RequestOptions): Promise<T> {
    const { requestOptions } = this.options;

    if (requestOptions.throttle !== undefined && requestOptions.debounce !== undefined) {
      throw new Error('throttle and debounce cannot be set at the same time');
    }

    if (requestOptions.throttle && requestOptions.throttle.delay !== 0) {
      return new Promise((resolve) => {
        throttle(() => resolve(this.synthesisRequest(config, options)), requestOptions.throttle.delay);
      });
    }

    if (requestOptions.debounce && requestOptions.debounce.delay !== 0) {
      return new Promise((resolve) => {
        debounce(() => resolve(this.synthesisRequest(config, options)), requestOptions.debounce.delay);
      });
    }

    return this.synthesisRequest(config, options);
  }

  /**
   * 请求方法
   * @private
   */
  private async synthesisRequest<T = any>(config: AxiosRequestConfigRetry, options?: RequestOptions): Promise<T> {
    let conf: CreateAxiosOptions = cloneDeep(config);
    const transform = this.getTransform();

    const { requestOptions } = this.options;

    const opt: RequestOptions = { ...requestOptions, ...options };

    const { beforeRequestHook, requestCatchHook, transformRequestHook } = transform || {};
    if (beforeRequestHook && isFunction(beforeRequestHook)) {
      conf = beforeRequestHook(conf, opt);
    }
    conf.requestOptions = opt;

    conf = this.supportFormData(conf);
    // 支持params数组参数格式化，因axios默认的toFormData即为brackets方式，无需配置paramsSerializer为qs，有需要可解除注释，参数参考qs文档
    // conf = this.supportParamsStringify(conf);

    return new Promise((resolve, reject) => {
      this.instance
        .request<any, AxiosResponse<Result>>(!config.retryCount ? conf : config)
        .then((res: AxiosResponse<Result>) => {
          if (transformRequestHook && isFunction(transformRequestHook)) {
            try {
              const ret = transformRequestHook(res, opt);
              resolve(ret);
            } catch (err) {
              reject(err || new Error('请求错误!'));
            }
            return;
          }
          resolve(res as unknown as Promise<T>);
        })
        .catch((e: Error | AxiosError) => {
          if (requestCatchHook && isFunction(requestCatchHook)) {
            reject(requestCatchHook(e, opt));
            return;
          }
          if (axios.isAxiosError(e)) {
            // 在这里重写Axios的错误信息
          }
          reject(e);
        });
    });
  }
}
