#  Copyright (c) 2024 Aaron Janeiro Stone
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from setuptools import setup

setup(
    name='vcx_py',
    version='1.0.6',
    packages=['vcx_py'],
    license='MIT',
    author='Aaron Janeiro Stone',
    author_email='aaron@thequant.ca',
    description='A simple python client for the VirgoCX API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.github.com/aarjaneiro/vcx_py'
)
