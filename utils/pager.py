from django.utils.safestring import mark_safe

#Pagination(data_show_number, current_page_num, all_num_count,page_num_show)
class Pagination:

    def __init__(self,current_page_num,all_num_count,get_data,page_num_show=5,data_show_number=20):
        """
        :param data_show_number:  每页显示多少条数据
        :param current_page_num:   当前访问的页码
        :param all_num_count:  总数据量
        :param get_data:   查询参数
        :param page_num_show:  html页面中显示多少个页码
        """
        self.data_show_number = data_show_number # 10
        self.page_num_show = page_num_show  # 7
        self.get_data = get_data


        try:
            self.current_page_num = int(current_page_num)
        except Exception:
            self.current_page_num = 1

        # data_show_number = 10  # 每页显示10条

        a, b = divmod(all_num_count, self.data_show_number)

        # page_num_count 就是咱们的总的页码数量
        if b:
            self.page_num_count = a + 1
        else:
            if a:
                self.page_num_count = a
            else:
                self.page_num_count = 1

        # 当用户访问的当前页面小于等于0时,让当前页面等于1
        if self.current_page_num <= 0:
            self.current_page_num = 1
        # 当用户访问的当前页面大于等于总页码数时,让当前页面等于总页码数
        if self.current_page_num >= self.page_num_count:
            self.current_page_num = self.page_num_count

        # page_num_show = 7  # 前端html页面显示的页码数量

        half_num = page_num_show // 2  # 7

        self.start_page_num = self.current_page_num - half_num  # 4 page_num_range = range(4-3,4+4)  -2
        self.end_page_num = self.current_page_num + half_num + 1


        if self.end_page_num >= self.page_num_count:
            self.end_page_num = self.page_num_count + 1  # 6
            self.start_page_num = self.end_page_num - self.page_num_show #-2

        # 当总页码数小于我们要展示的页码数时,就展示总的页码数
        if self.page_num_count < self.page_num_show:
            self.start_page_num = 1
            self.end_page_num = self.page_num_count + 1 # 6

        if self.start_page_num <= 0:
            self.start_page_num = 1
            self.end_page_num = self.page_num_show + 1


        self.page_num_range = range(self.start_page_num, self.end_page_num)  #[-1,0,1,2,3,4,5]

    @property
    def start_data_num(self):
        return (self.current_page_num - 1) * self.data_show_number

    @property
    def end_data_num(self):

        return self.current_page_num * self.data_show_number

    def html(self):
        page_html = '''
                <nav aria-label="Page navigation example">
                  <ul class="pagination">
            '''

        # 首页
        # if self.current_page_num <= self.page_num_count-self.start_data_num:
        if self.current_page_num <= 1:
            self.get_data['page'] = 1
            first_page = f'''
                        <li class="page-item disabled">
                          <a class="page-link" href="?{self.get_data.urlencode()}" aria-label="Previous">
                            <span aria-hidden="true">首页</span>
                          </a>
                        </li>
                '''
        else:
            self.get_data['page'] = 1
            first_page = f'''
                                   <li class="page-item">
                                     <a class="page-link" href="?{self.get_data.urlencode()}" aria-label="Previous">
                                       <span aria-hidden="true">首页</span>
                                     </a>
                                   </li>
                           '''
        page_html += first_page
        # 上一页


        if self.current_page_num <= 1:
            self.get_data['page'] = self.current_page_num-1
            prev_page = f'''
                        <li class="page-item disabled">
                          <a class="page-link" href="?{self.get_data.urlencode()}" aria-label="Previous">
                            <span aria-hidden="true">&laquo;</span>
                          </a>
                        </li>
                '''
        else:
            self.get_data['page'] = self.current_page_num - 1
            prev_page = f'''
                                <li class="page-item">
                                  <a class="page-link" href="?{self.get_data.urlencode()}" aria-label="Previous">
                                    <span aria-hidden="true">&laquo;</span>
                                  </a>
                                </li>
                        '''

        page_html += prev_page

        html = ''
        for page_num in self.page_num_range: #[-1,0,1,2,3,4,5]
            self.get_data['page'] = page_num

            if page_num == self.current_page_num:

                html += f'''<li class="page-item active"><a class="page-link" href="?{self.get_data.urlencode()}">{ page_num }</a></li>
                
            '''
            else:
                html += f'''<li class="page-item"><a class="page-link" href="?{self.get_data.urlencode()}">{ page_num }</a></li>'''

        page_html += html

        if self.current_page_num >= self.page_num_count:
            self.get_data['page'] = self.current_page_num + 1
            next_page = f'''
                        <li class="page-item disabled">
                          <a class="page-link" href="?{self.get_data.urlencode()}" aria-label="Next">
                            <span aria-hidden="true">&raquo;</span>
                          </a>
                        </li>
                '''
        else:
            self.get_data['page'] = self.current_page_num + 1
            next_page = f'''
                                <li class="page-item">
                                  <a class="page-link" href="?{self.get_data.urlencode()}" aria-label="Next">
                                    <span aria-hidden="true">&raquo;</span>
                                  </a>
                                </li>
                        '''
        page_html += next_page

        if self.current_page_num >= self.page_num_count:
            self.get_data['page'] = self.page_num_count
            last_page = f'''
                            <li class="page-item disabled">
                              <a class="page-link" href="?{self.get_data.urlencode()}" aria-label="Next">
                                <span aria-hidden="true">尾页</span>
                              </a>
                            </li>
                            </ul>
                        </nav>
                    '''
        else:
            self.get_data['page'] = self.page_num_count
            last_page = f'''
                                    <li class="page-item">
                                      <a class="page-link" href="?{self.get_data.urlencode()}" aria-label="Next">
                                        <span aria-hidden="true">尾页</span>
                                      </a>
                                    </li>
                                    </ul>
                                </nav>
                            '''
        page_html += last_page

        return mark_safe(page_html)








