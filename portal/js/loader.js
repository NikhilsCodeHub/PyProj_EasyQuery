  // html component loader 


    function init_sidebar()
    {
        console.log("sidebar initialized");
        /*======== 4. SIDEBAR TOGGLE FOR MOBILE ========*/
        if ($(window).width() < 768) {
            $(document).on("click", ".sidebar-toggle", function (e) {
            e.preventDefault();
            var min = "sidebar-mobile-in",
                min_out = "sidebar-mobile-out",
                body = "#body";
            $(body).hasClass(min)
                ? $(body).removeClass(min).addClass(min_out)
                : $(body).addClass(min).removeClass(min_out);
            });
        }

        /*======== 5. SIDEBAR TOGGLE FOR VARIOUS SIDEBAR LAYOUT ========*/
        var body = $("#body");
        if ($(window).width() >= 768) {
            if (body.hasClass("sidebar-mobile-in sidebar-mobile-out")) {
            body.removeClass("sidebar-mobile-in sidebar-mobile-out");
            }

            window.isMinified = false;
            window.isCollapsed = false;

            $("#sidebar-toggler").on("click", function () {
            //console.log("Toggle Clicked")
            if (
                body.hasClass("sidebar-fixed-offcanvas") ||
                body.hasClass("sidebar-static-offcanvas")
            ) {
                $(this)
                .addClass("sidebar-offcanvas-toggle")
                .removeClass("sidebar-toggle");
                if (window.isCollapsed === false) {
                body.addClass("sidebar-collapse");
                window.isCollapsed = true;
                window.isMinified = false;
                } else {
                body.removeClass("sidebar-collapse");
                body.addClass("sidebar-collapse-out");
                setTimeout(function () {
                    body.removeClass("sidebar-collapse-out");
                }, 300);
                window.isCollapsed = false;
                }
            }

            if (body.hasClass("sidebar-fixed") || body.hasClass("sidebar-static")) {
                $(this)
                .addClass("sidebar-toggle")
                .removeClass("sidebar-offcanvas-toggle");
                if (window.isMinified === false) {
                body
                    .removeClass("sidebar-collapse sidebar-minified-out")
                    .addClass("sidebar-minified");
                window.isMinified = true;
                window.isCollapsed = false;
                } else {
                body.removeClass("sidebar-minified");
                body.addClass("sidebar-minified-out");
                window.isMinified = false;
                }
            }
            });
        }

        if ($(window).width() >= 768 && $(window).width() < 992) {
            if (body.hasClass("sidebar-fixed") || body.hasClass("sidebar-static")) {
            body
                .removeClass("sidebar-collapse sidebar-minified-out")
                .addClass("sidebar-minified");
            window.isMinified = true;
            }
        }
    }

    function load_sidebar_dataset()
    {
      fetch('sidebar.html')
        .then(response => response.text())
        .then(data => {
          //console.log(document.getElementById('sidebar-container').innerHTML);
          document.getElementById('sidebar-container').outerHTML = data;
          console.log("Sidebar Loaded");
        })
        .catch(error => console.error('Error loading sidebar:', error));

        fetch('dataset.html')
        .then(response => response.text())
        .then(data => {
          //console.log(document.getElementById('sidebar-container').innerHTML);
          document.getElementById('dataset-container').innerHTML = data;
        })
        .catch(error => console.error('Error loading sidebar:', error));
        
        init_sidebar();   // ---- Initialize the Sidebar

        // -- highlight the menu item
        setTimeout(highlight_menu,100);
      
    }

    function highlight_menu()
    {
        if (window.location.pathname.includes("index"))
        {   
            document.getElementById("mnu_intro").parentElement.className = "active";
        }
        else if (window.location.pathname.includes("demo"))
        {
            document.getElementById("mnu_demo").parentElement.className = "active"
        }
        else if (window.location.pathname.includes("design"))
        {
            document.getElementById("mnu_design").parentElement.className = "active"
        }  
    }