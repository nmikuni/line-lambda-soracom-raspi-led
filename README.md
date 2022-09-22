# Sample program to control Raspberry Pi LED from LINE via AWS Lambda and Soracom

Raspberry Pi の LED を LINE から AWS Lambda と SORACOM 経由で操作するサンプルコードです。

使い方は [LINE から Raspberry Pi の LED を操作する 3 つのパターンを試した - Qiita](https://qiita.com/n_mikuni/private/b4bfb5752147639fc1c7) で紹介しています。

LINE から AWS Lambda を呼び出す方法としては、以下のサーバーワークス様のブログをほとんどそのまま使わせていただき、SQS を間に挟む構成としています。当リポジトリや上記のブログはサーバーワーク様に許可をいただいてコードの引用・公開をしています。

[【入門編①】Serverless Framework で 「おうむ返し」LINE Bot を作る - サーバーワークスエンジニアブログ](https://blog.serverworks.co.jp/sls-line-beginner)
