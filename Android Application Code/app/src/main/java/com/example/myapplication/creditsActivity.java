package com.example.myapplication;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.view.View;

public class creditsActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle("CREDITS");
        setContentView(R.layout.activity_credits_);
    }

    public void returnToPreviousActivity(View view) {
        this.finish();
    }
}
