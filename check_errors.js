#!/usr/bin/env node
/**
 * Puppeteerを使用してページのエラーを収集するスクリプト
 */

const puppeteer = require('puppeteer-core');

async function collectErrors(url) {
  let browser;
  const errors = {
    console_messages: [],
    network_errors: []
  };

  try {
    // 既存のChromeインスタンスに接続
    browser = await puppeteer.connect({
      browserURL: 'http://localhost:9222',
      defaultViewport: null
    });

    const page = await browser.newPage();

    // コンソールメッセージを収集
    page.on('console', msg => {
      const type = msg.type();
      if (type === 'error' || type === 'warning') {
        errors.console_messages.push({
          level: type,
          text: msg.text(),
          location: msg.location()
        });
      }
    });

    // ページエラーを収集
    page.on('pageerror', error => {
      errors.console_messages.push({
        level: 'error',
        text: error.toString(),
        location: {}
      });
    });

    // ネットワークレスポンスを監視
    page.on('response', response => {
      const status = response.status();
      if (status >= 400) {
        errors.network_errors.push({
          url: response.url(),
          status: status,
          statusText: response.statusText()
        });
      }
    });

    // ページにナビゲート
    console.error(`ページ読み込み中: ${url}`);
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    console.error('ページ読み込み完了');

    // 最終URLとページタイトルを取得
    const finalUrl = page.url();
    const pageTitle = await page.title();
    console.error(`最終URL: ${finalUrl}`);
    console.error(`ページタイトル: ${pageTitle}`);

    // 追加のエラーを収集するために少し待機
    await new Promise(resolve => setTimeout(resolve, 2000));

    // メタ情報を追加
    errors.page_info = {
      final_url: finalUrl,
      title: pageTitle
    };

  } catch (error) {
    console.error(`エラー発生: ${error.message}`);
    errors.console_messages.push({
      level: 'error',
      text: `Script error: ${error.message}`,
      location: {}
    });
  } finally {
    if (browser) {
      await browser.disconnect();
    }
  }

  return errors;
}

(async () => {
  const url = process.argv[2] || 'https://s-style-hrd.appspot.com/test/';
  const errors = await collectErrors(url);
  console.log(JSON.stringify(errors, null, 2));
})();
