package com.example.myapplication;

import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.app.ProgressDialog;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;

public class connectionsActivity extends AppCompatActivity {
    ProgressDialog pd;
    ImageView iv;
    TextView tv;
    @SuppressLint("SetTextI18n")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle("CONNECTION");
        setContentView(R.layout.activity_connections);
        pd = new ProgressDialog(this);
        iv = findViewById(R.id.statusLight);
        tv = findViewById(R.id.statusText);
        if(methodsActivity.port!=0){
            float scale = getResources().getDisplayMetrics().density;
            int dpAsPixelsStart = (int) (170*scale + 0.5f);
            int dpAsPixelsEnd = (int) (32*scale + 0.5f);
            tv.setPadding(dpAsPixelsStart,0,dpAsPixelsEnd,0);
            tv.setText("Connected");
            iv.setImageResource(R.drawable.onlight);
        }
    }
    @SuppressLint("SetTextI18n")
    public void connectToRobot(View view) {
        pd.setMessage("Connecting");
        pd.show();
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                pd.dismiss();
            }
        }, 1000);
        float scale = getResources().getDisplayMetrics().density;
        int dpAsPixelsStart = (int) (170*scale + 0.5f);
        int dpAsPixelsEnd = (int) (32*scale + 0.5f);
        tv.setPadding(dpAsPixelsStart,0,dpAsPixelsEnd,0);
        tv.setText("Connected");
        iv.setImageResource(R.drawable.onlight);
        methodsActivity.localhost="192.168.8.119";
        methodsActivity.port=26968;
    }

    @SuppressLint("SetTextI18n")
    public void disconnectRobot(View view) {
        float scale = getResources().getDisplayMetrics().density;
        int dpAsPixelsStart = (int) (190*scale + 0.5f);
        int dpAsPixelsEnd = (int) (39*scale + 0.5f);
        tv.setPadding(dpAsPixelsStart,0,dpAsPixelsEnd,0);
        tv.setText("Waiting");
        iv.setImageResource(R.drawable.offlight);
        methodsActivity.localhost="";
        methodsActivity.port=0;
    }

    public void returnToPreviousActivity(View view) {
        this.finish();
    }
}
