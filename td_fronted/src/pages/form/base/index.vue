<template>
  <t-form
    ref="form"
    class="base-form"
    :data="formData"
    :rules="FORM_RULES"
    label-align="top"
    :label-width="100"
    @reset="onReset"
    @submit="onSubmit"
  >
    <div class="form-basic-container">
      <div class="form-basic-item">
        <div class="form-basic-container-title">{{ t('pages.formBase.title') }}</div>
        <!-- 表单内容 -->

        <!-- 合同名称,合同类型 -->
        <t-row class="row-gap" :gutter="[32, 24]">
          <t-col :span="6">
            <t-form-item :label="t('pages.formBase.contractName')" name="name">
              <t-input v-model="formData.name" :style="{ width: '322px' }" placeholder="请输入内容" />
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item :label="t('pages.formBase.contractType')" name="type">
              <t-select v-model="formData.type" :style="{ width: '322px' }" class="demo-select-base" clearable>
                <t-option v-for="(item, index) in TYPE_OPTIONS" :key="index" :value="item.value" :label="item.label">
                  {{ item.label }}
                </t-option>
              </t-select>
            </t-form-item>
          </t-col>

          <!-- 合同收付类型 -->
          <t-col :span="8">
            <t-form-item :label="t('pages.formBase.contractPayType')" name="payment">
              <t-radio-group v-model="formData.payment">
                <t-radio value="1"> {{ t('pages.formBase.receive') }} </t-radio>
                <t-radio value="2"> {{ t('pages.formBase.pay') }} </t-radio>
              </t-radio-group>
              <span class="space-item" />
              <div>
                <t-input :placeholder="t('pages.formBase.contractAmountPlaceholder')" :style="{ width: '160px' }" />
              </div>
            </t-form-item>
          </t-col>

          <t-col :span="6">
            <t-form-item :label="t('pages.formBase.company')" name="partyA">
              <t-select
                v-model="formData.partyA"
                :style="{ width: '322px' }"
                class="demo-select-base"
                :placeholder="t('pages.formBase.contractTypePlaceholder')"
                clearable
              >
                <t-option v-for="(item, index) in PARTY_A_OPTIONS" :key="index" :value="item.value" :label="item.label">
                  {{ item.label }}
                </t-option>
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item :label="t('pages.formBase.employee')" name="partyB">
              <t-select
                v-model="formData.partyB"
                :style="{ width: '322px' }"
                :placeholder="t('pages.formBase.contractTypePlaceholder')"
                class="demo-select-base"
                clearable
              >
                <t-option v-for="(item, index) in PARTY_B_OPTIONS" :key="index" :value="item.value" :label="item.label">
                  {{ item.label }}
                </t-option>
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item :label="t('pages.formBase.contractSignDate')" name="signDate">
              <t-date-picker
                v-model="formData.signDate"
                :style="{ width: '322px' }"
                theme="primary"
                mode="date"
                separator="/"
              />
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item :label="t('pages.formBase.contractEffectiveDate')" name="startDate">
              <t-date-picker
                v-model="formData.startDate"
                :style="{ width: '322px' }"
                theme="primary"
                mode="date"
                separator="/"
              />
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item :label="t('pages.formBase.contractEndDate')" name="endDate">
              <t-date-picker
                v-model="formData.endDate"
                :style="{ width: '322px' }"
                theme="primary"
                mode="date"
                separator="/"
              />
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item :label="t('pages.formBase.upload')" name="files">
              <t-upload
                v-model="formData.files"
                action="https://service-bv448zsw-1257786608.gz.apigw.tencentcs.com/api/upload-demo"
                :tips="t('pages.formBase.uploadTips')"
                :size-limit="{ size: 60, unit: 'MB' }"
                :format-response="formatResponse"
                :before-upload="beforeUpload"
                @fail="handleFail"
              >
                <t-button class="form-submit-upload-btn" variant="outline">
                  {{ t('pages.formBase.uploadFile') }}
                </t-button>
              </t-upload>
            </t-form-item>
          </t-col>
        </t-row>

        <div class="form-basic-container-title form-title-gap">{{ t('pages.formBase.otherInfo') }}</div>

        <t-form-item :label="t('pages.formBase.remark')" name="comment">
          <t-textarea v-model="formData.comment" :height="124" :placeholder="t('pages.formBase.remarkPlaceholder')" />
        </t-form-item>
        <t-form-item :label="t('pages.formBase.notaryPublic')">
          <t-avatar-group>
            <t-avatar>D</t-avatar>
            <t-avatar>S</t-avatar>
            <t-avatar>+</t-avatar>
          </t-avatar-group>
        </t-form-item>
      </div>
    </div>

    <div class="form-submit-container">
      <div class="form-submit-sub">
        <div class="form-submit-left">
          <t-button theme="primary" class="form-submit-confirm" type="submit">
            {{ t('pages.formBase.confirm') }}
          </t-button>
          <t-button type="reset" class="form-submit-cancel" theme="default" variant="base">
            {{ t('pages.formBase.cancel') }}
          </t-button>
        </div>
      </div>
    </div>
  </t-form>
</template>

<script lang="ts">
export default {
  name: 'FormBase',
};
</script>

<script setup lang="ts">
import type { SubmitContext, UploadFailContext, UploadFile } from 'tdesign-vue-next';
import { MessagePlugin } from 'tdesign-vue-next';
import { ref } from 'vue';

import { t } from '@/locales';

import { FORM_RULES, INITIAL_DATA, PARTY_A_OPTIONS, PARTY_B_OPTIONS, TYPE_OPTIONS } from './constants';

const formData = ref({ ...INITIAL_DATA });

const onReset = () => {
  MessagePlugin.warning('取消新建');
};
const onSubmit = (ctx: SubmitContext) => {
  if (ctx.validateResult === true) {
    MessagePlugin.success('新建成功');
  }
};
const beforeUpload = (file: UploadFile) => {
  if (!/\.(pdf)$/.test(file.name)) {
    MessagePlugin.warning('请上传pdf文件');
    return false;
  }
  if (file.size > 60 * 1024 * 1024) {
    MessagePlugin.warning('上传文件不能大于60M');
    return false;
  }
  return true;
};
const handleFail = (options: UploadFailContext) => {
  MessagePlugin.error(`文件 ${options.file.name} 上传失败`);
};
// 用于格式化接口响应值，error 会被用于上传失败的提示文字；url 表示文件/图片地址
const formatResponse = (res: any) => {
  return { ...res, error: '上传失败，请重试', url: res.url };
};
</script>

<style lang="less" scoped>
@import './index.less';
</style>
