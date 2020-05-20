package com.example.myapplication;

import android.animation.ObjectAnimator;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.view.animation.DecelerateInterpolator;
import android.widget.ProgressBar;

import androidx.appcompat.app.AppCompatActivity;

public class splashScreen extends AppCompatActivity {
    ProgressBar pb;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splashscreen);
    }
    @Override
    public void onAttachedToWindow() {
        super.onAttachedToWindow();
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                startProgress();
            }
        }, 500);
    }

    private void startProgress() {
        pb = findViewById(R.id.pb);
        pb.setScaleY(1);
        pb.setProgressTintList(ColorStateList.valueOf(Color.rgb(44,49,99)));
        pb.setMax(100 * 100);
        ObjectAnimator animation = ObjectAnimator.ofInt(pb, "progress", pb.getProgress(), 100 * 100);
        animation.setDuration(2000);
        animation.setInterpolator(new DecelerateInterpolator());
        animation.start();
        final Intent i = new Intent(this, mainActivity.class);
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                startActivity(i);
                finishActivity();
            }
        }, 2000);
    }
    private void finishActivity(){
        this.finish();
    }
}
