import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { AxiosError } from 'axios';

import type { RequestOptions, Result } from '@/types/axios';

/**
 * @description 创建Axios实例配置
 */
export interface CreateAxiosOptions extends AxiosRequestConfig {
  /**
   * 请求验证方案
   *
   * https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#authentication_schemes
   */
  authenticationScheme?: string;
  /**
   * 请求数据处理
   */
  transform?: AxiosTransform;
  /**
   * 请求配置
   */
  requestOptions?: RequestOptions;
}

/**
 * Axios请求数据处理 抽象类
 */
export abstract class AxiosTransform {
  /**
   * 请求前钩子
   */
  beforeRequestHook?: (config: AxiosRequestConfig, options: RequestOptions) => AxiosRequestConfig;

  /**
   * 数据处理前钩子
   */
  transformRequestHook?: <T = any>(res: AxiosResponse<Result>, options: RequestOptions) => T;

  /**
   * 请求失败钩子
   */
  requestCatchHook?: <T = any>(e: Error | AxiosError, options: RequestOptions) => Promise<T>;

  /**
   * 请求拦截器
   */
  requestInterceptors?: (config: AxiosRequestConfig, options: CreateAxiosOptions) => AxiosRequestConfig;

  /**
   * 响应拦截器
   */
  responseInterceptors?: (res: AxiosResponse) => AxiosResponse;

  /**
   * 请求拦截器错误处理
   */
  requestInterceptorsCatch?: (error: AxiosError) => void;

  /**
   * 响应拦截器错误处理
   */
  responseInterceptorsCatch?: (error: AxiosError, instance: AxiosInstance) => void;
}
