package com.baiworkspace.notifyapp

import android.app.Activity
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Notification
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.TextView

class MainActivity : Activity() {

    private val channelId = "default_channel"
    private val permissionRequestCode = 100
    private var notificationCount = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        createNotificationChannel()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), permissionRequestCode)
        }

        findViewById<Button>(R.id.notifyButton).setOnClickListener {
            showNotification()
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "기본 알림",
                NotificationManager.IMPORTANCE_HIGH
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun showNotification() {
        notificationCount += 1

        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = Notification.Builder(this, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("테스트 알림 #$notificationCount")
            .setContentText("버튼을 눌러서 발생한 알림입니다")
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        try {
            val manager = getSystemService(NotificationManager::class.java)
            manager.notify(notificationCount, notification)
            findViewById<TextView>(R.id.statusText).text = "알림 ${notificationCount}개 보냄"
        } catch (e: SecurityException) {
            findViewById<TextView>(R.id.statusText).text = "알림 권한이 없습니다"
        }
    }
}
