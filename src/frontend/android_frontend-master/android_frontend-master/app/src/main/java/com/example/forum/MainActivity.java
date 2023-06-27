package com.example.forum;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentContainerView;

import android.annotation.SuppressLint;
import android.os.Bundle;
import android.view.MenuItem;

import com.example.forum.fragment.BlankFragment;
import com.example.forum.fragment.HomeFragment;
import com.example.forum.fragment.NoticeFragment;
import com.example.forum.fragment.ProfileFragment;
import com.example.forum.fragment.TopicFragment;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.google.android.material.navigation.NavigationBarView;

import java.util.ArrayList;

public class MainActivity extends AppCompatActivity {

    BottomNavigationView navigationView;
    FragmentContainerView containerView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        navigationView = findViewById(R.id.menuViewID);
        containerView = findViewById(R.id.containerID);
        ArrayList<Fragment> fragmentList = new ArrayList<>();
        HomeFragment homeFragment = new HomeFragment();

        fragmentList.add(homeFragment);
        fragmentList.add(TopicFragment.newInstance("话题", ""));
        fragmentList.add(NoticeFragment.newInstance("通知", ""));
        fragmentList.add(ProfileFragment.newInstance("我的", ""));

        navigationView.setOnItemSelectedListener(new NavigationBarView.OnItemSelectedListener() {
            @SuppressLint("NonConstantResourceId")
            @Override
            public boolean onNavigationItemSelected(@NonNull MenuItem item) {
                int itemId = item.getItemId();
                switch (itemId) {
                    case R.id.menu_nav_home:
                        getSupportFragmentManager().beginTransaction()
                                .replace(R.id.containerID, fragmentList.get(0))
                                .commit();
                        break;
                    case R.id.menu_nav_topics:
                        getSupportFragmentManager().beginTransaction()
                                .replace(R.id.containerID, fragmentList.get(1))
                                .commit();
                        break;
                    case R.id.menu_nav_introduction:
                        getSupportFragmentManager().beginTransaction()
                                .replace(R.id.containerID, fragmentList.get(2))
                                .commit();
                        break;
                    case R.id.menu_nav_profile:
                        getSupportFragmentManager().beginTransaction()
                                .replace(R.id.containerID, fragmentList.get(3))
                                .commit();
                }
                return true;
            }
        });
        getSupportFragmentManager().beginTransaction()
                .replace(R.id.containerID, fragmentList.get(0))
                .commit();


    }
}